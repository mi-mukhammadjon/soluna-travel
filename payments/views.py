import uuid
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from bookings.models import Booking
from .models import Payment
from .click import generate_click_url, verify_click_signature
from .payme import generate_payme_url, verify_payme_auth, PAYME_ERRORS


class PaymentSelectView(LoginRequiredMixin, View):
    """To'lov usulini tanlash sahifasi"""

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
        if booking.status not in ('pending', 'confirmed'):
            messages.error(request, "Bu bron uchun to'lov qilib bo'lmaydi.")
            return redirect('bookings:booking-detail', pk=booking_id)
        return render(request, 'payments/select.html', {'booking': booking})

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
        provider = request.POST.get('provider')

        if provider not in ('click', 'payme'):
            messages.error(request, "Noto'g'ri to'lov usuli.")
            return redirect('payments:select', booking_id=booking_id)

        # USD ni UZS ga o'girish (taxminiy kurs)
        usd_rate = 12700
        amount_uzs = booking.total_price * usd_rate

        payment = Payment.objects.create(
            booking=booking,
            provider=provider,
            amount=amount_uzs,
            currency='UZS',
            transaction_id=f"BK{booking.booking_number}-{uuid.uuid4().hex[:8].upper()}",
        )

        if provider == 'click':
            url = generate_click_url(booking, payment)
        else:
            url = generate_payme_url(booking, payment)

        return redirect(url)


class ClickReturnView(LoginRequiredMixin, View):
    """Click to'lovidan qaytish"""

    def get(self, request):
        transaction_id = request.GET.get('merchant_trans_id')
        error = request.GET.get('error', '0')

        if not transaction_id:
            return redirect('home')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            if error == '0':
                payment.status = 'success'
                payment.paid_at = timezone.now()
                payment.booking.status = 'confirmed'
                payment.booking.save()
                messages.success(request, "To'lov muvaffaqiyatli amalga oshirildi!")
            else:
                payment.status = 'failed'
                messages.error(request, "To'lov amalga oshmadi.")
            payment.save()
            return redirect('bookings:booking-detail', pk=payment.booking.pk)
        except Payment.DoesNotExist:
            return redirect('home')


@method_decorator(csrf_exempt, name='dispatch')
class ClickWebhookView(View):
    """Click server-to-server webhook"""

    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        if not verify_click_signature(data):
            return JsonResponse({'error': -1, 'error_note': 'Invalid sign'})

        action = int(data.get('action', -1))
        transaction_id = data.get('merchant_trans_id')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': -5, 'error_note': 'Transaction not found'})

        if action == 0:
            # Prepare — to'lovni tayyorlash
            payment.status = 'waiting'
            payment.save()
            return JsonResponse({
                'click_trans_id': data.get('click_trans_id'),
                'merchant_trans_id': transaction_id,
                'merchant_prepare_id': payment.pk,
                'error': 0,
                'error_note': 'Success',
            })

        elif action == 1:
            # Complete — to'lovni tasdiqlash
            payment.status = 'success'
            payment.paid_at = timezone.now()
            payment.provider_transaction_id = data.get('click_trans_id', '')
            payment.provider_response = data
            payment.save()
            payment.booking.status = 'confirmed'
            payment.booking.save()
            return JsonResponse({
                'click_trans_id': data.get('click_trans_id'),
                'merchant_trans_id': transaction_id,
                'merchant_confirm_id': payment.pk,
                'error': 0,
                'error_note': 'Success',
            })

        return JsonResponse({'error': -3, 'error_note': 'Invalid action'})


@method_decorator(csrf_exempt, name='dispatch')
class PaymeWebhookView(View):
    """Payme server-to-server webhook (JSON-RPC 2.0)"""

    def post(self, request):
        import json

        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not verify_payme_auth(auth):
            return JsonResponse({
                'error': {'code': -32504, 'message': {'uz': 'Token not found', 'ru': 'Токен не найден', 'en': 'Token not found'}},
                'id': None
            }, status=401)

        try:
            body = json.loads(request.body)
        except Exception:
            return JsonResponse({'error': {'code': -32700, 'message': PAYME_ERRORS[-32700]}, 'id': None})

        method = body.get('method')
        params = body.get('params', {})
        rpc_id = body.get('id')

        if method == 'CheckPerformTransaction':
            order_id = params.get('account', {}).get('booking_id')
            try:
                booking = Booking.objects.get(pk=order_id)
                return JsonResponse({'result': {'allow': True}, 'id': rpc_id})
            except Exception:
                return JsonResponse({'error': {'code': -31050, 'message': PAYME_ERRORS[-31050]}, 'id': rpc_id})

        elif method == 'CreateTransaction':
            order_id = params.get('account', {}).get('booking_id')
            payme_id = params.get('id')
            amount = params.get('amount', 0) / 100  # tiyindan so'mga

            try:
                from bookings.models import Booking as BookingModel
                booking = BookingModel.objects.get(pk=order_id)
                payment, _ = Payment.objects.get_or_create(
                    provider_transaction_id=payme_id,
                    defaults={
                        'booking': booking,
                        'provider': 'payme',
                        'amount': amount,
                        'currency': 'UZS',
                        'transaction_id': f"PAYME-{payme_id[:16]}",
                        'status': 'waiting',
                    }
                )
                return JsonResponse({
                    'result': {
                        'create_time': int(payment.created_at.timestamp() * 1000),
                        'transaction': str(payment.pk),
                        'state': 1,
                    },
                    'id': rpc_id
                })
            except Exception:
                return JsonResponse({'error': {'code': -31050, 'message': PAYME_ERRORS[-31050]}, 'id': rpc_id})

        elif method == 'PerformTransaction':
            payme_id = params.get('id')
            try:
                payment = Payment.objects.get(provider_transaction_id=payme_id)
                payment.status = 'success'
                payment.paid_at = timezone.now()
                payment.save()
                payment.booking.status = 'confirmed'
                payment.booking.save()
                return JsonResponse({
                    'result': {
                        'transaction': str(payment.pk),
                        'perform_time': int(timezone.now().timestamp() * 1000),
                        'state': 2,
                    },
                    'id': rpc_id
                })
            except Exception:
                return JsonResponse({'error': {'code': -31050, 'message': PAYME_ERRORS[-31050]}, 'id': rpc_id})

        elif method == 'CancelTransaction':
            payme_id = params.get('id')
            try:
                payment = Payment.objects.get(provider_transaction_id=payme_id)
                payment.status = 'cancelled'
                payment.save()
                return JsonResponse({
                    'result': {
                        'transaction': str(payment.pk),
                        'cancel_time': int(timezone.now().timestamp() * 1000),
                        'state': -1,
                    },
                    'id': rpc_id
                })
            except Exception:
                return JsonResponse({'error': {'code': -31050, 'message': PAYME_ERRORS[-31050]}, 'id': rpc_id})

        return JsonResponse({'error': {'code': -32601, 'message': PAYME_ERRORS[-32601]}, 'id': rpc_id})