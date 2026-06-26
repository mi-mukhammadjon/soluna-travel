# payments/views.py
import json
import logging
import time
from decimal import Decimal
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from bookings.models import Booking
from .models import Payment, Currency

logger = logging.getLogger('payments')


def is_mock_mode():
    """Click YOKI Payme kalitlari yo'q bo'lsa — mock rejim"""
    return not (
        getattr(settings, 'CLICK_MERCHANT_ID', '')
        or getattr(settings, 'PAYME_MERCHANT_ID', '')
    )


class PaymentSelectView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = get_object_or_404(
            Booking, pk=kwargs['booking_id'], user=self.request.user,
        )
        try:
            amount_uzs = Currency.convert(booking.total_price, from_code=booking.currency, to_code='UZS')
        except Exception:
            amount_uzs = Decimal(str(booking.total_price)) * Decimal('12700')
        context['booking'] = booking
        context['amount_uzs'] = int(amount_uzs)
        context['amount_uzs_formatted'] = f"{int(amount_uzs):,}".replace(',', ' ')
        context['is_mock'] = is_mock_mode()
        return context


class PaymentInitiateView(LoginRequiredMixin, View):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

        if booking.status != 'pending':
            messages.warning(request, _("Bu bron uchun to'lov allaqachon qabul qilingan."))
            return redirect('bookings:booking-detail', pk=booking.id)

        method = request.POST.get('method', 'click')

        try:
            amount_uzs = Currency.convert(booking.total_price, from_code=booking.currency, to_code='UZS')
            uzs_currency = Currency.objects.get(code='UZS', is_active=True)
            rate = uzs_currency.rate_to_usd
        except Currency.DoesNotExist:
            rate = Decimal('12700')
            amount_uzs = Decimal(str(booking.total_price)) * rate

        with transaction.atomic():
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                method=method,
                status='created',
                amount_uzs=int(amount_uzs * 100),
                amount_usd=booking.total_price,
                exchange_rate=rate,
            )

        if method == 'cash':
            payment.status = 'pending'
            payment.save()
            messages.info(request, _("Ofisda to'lov qilishni tanladingiz."))
            return redirect('bookings:booking-detail', pk=booking.id)

        # ── BANK KARTA (Visa / Mastercard / UZCARD / HUMO) ──
        # To'g'ridan-to'g'ri xavfsiz karta kiritish formasiga olib boradi.
        if method == 'card':
            return redirect('payments:mock-pay', payment_id=payment.id)

        # ── MOCK REJIM ──
        if is_mock_mode():
            return redirect('payments:mock-pay', payment_id=payment.id)

        # ── REAL REJIM ──
        return_url = request.build_absolute_uri(
            reverse('payments:return', kwargs={'payment_id': payment.id})
        )
        try:
            if method == 'click':
                from .gateways.click import ClickService
                gateway_url = ClickService.generate_payment_url(payment, return_url=return_url)
            elif method == 'payme':
                from .gateways.payme import PaymeService
                gateway_url = PaymeService.generate_payment_url(payment, return_url=return_url)
            else:
                messages.error(request, _("Ushbu to'lov turi hali qo'llanilmaydi."))
                payment.mark_failed(reason='Method not supported')
                return redirect('payments:select', booking_id=booking.id)
        except Exception as e:
            import traceback
            logger.error(f"Gateway error: {e}\n{traceback.format_exc()}")
            messages.error(request, f"To'lov tizimida xatolik: {type(e).__name__}: {e}")
            payment.mark_failed(reason=str(e))
            return redirect('payments:select', booking_id=booking.id)

        return redirect(gateway_url)


# ── HELPERS ──

def luhn_valid(card_number):
    try:
        digits = [int(d) for d in card_number]
    except ValueError:
        return False
    odd = digits[-1::-2]
    even = digits[-2::-2]
    checksum = sum(odd)
    for d in even:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0


def detect_brand(card_number):
    if card_number.startswith('4'):
        return 'visa'
    if card_number[:2] in ('51', '52', '53', '54', '55'):
        return 'mastercard'
    if card_number[:2] in ('34', '37'):
        return 'amex'
    if card_number.startswith('8600'):
        return 'uzcard'
    if card_number.startswith('9860'):
        return 'humo'
    if card_number[:2] == '62':
        return 'unionpay'
    return 'unknown'


class MockPaymentView(LoginRequiredMixin, View):
    """Mock to'lov sahifasi — Click/Payme simulyatsiyasi"""
    template_name = 'payments/mock_pay.html'

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        if payment.status == 'paid':
            return redirect('payments:success', booking_id=payment.booking.id)
        return render(request, self.template_name, {'payment': payment})

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        if payment.status == 'paid':
            return redirect('payments:success', booking_id=payment.booking.id)

        card_number = request.POST.get('card_number', '').replace(' ', '')
        card_expiry = request.POST.get('card_expiry', '')
        card_cvv = request.POST.get('card_cvv', '')

        # Validatsiya
        if not card_number.isdigit() or not (13 <= len(card_number) <= 19):
            return render(request, self.template_name, {
                'payment': payment, 'error': "Karta raqami noto'g'ri (13-19 raqam).",
            })

        if not luhn_valid(card_number):
            return render(request, self.template_name, {
                'payment': payment, 'error': "Karta raqami yaroqsiz.",
            })

        if not card_expiry or '/' not in card_expiry:
            return render(request, self.template_name, {
                'payment': payment, 'error': "Yaroqlilik muddati MM/YY shaklida.",
            })

        if not card_cvv.isdigit() or not (3 <= len(card_cvv) <= 4):
            return render(request, self.template_name, {
                'payment': payment, 'error': "CVV 3-4 raqamdan iborat.",
            })

        time.sleep(1.5)  # Gateway taqlid

        brand = detect_brand(card_number)
        last4 = card_number[-4:]

        # Test cards
        if card_number == '4242424242424242':
            payment.card_brand = brand
            payment.card_last4 = last4
            payment.mark_paid(transaction_id=f'mock-{payment.id}', gateway_data={'mock': True, 'last4': last4})
            messages.success(request, "To'lov muvaffaqiyatli! (Mock mode)")
            return redirect('payments:success', booking_id=payment.booking.id)

        elif card_number == '4000000000000002':
            payment.mark_failed(reason='Card declined', gateway_data={'mock': True})
            return render(request, self.template_name, {
                'payment': payment, 'error': "Karta bank tomonidan rad etildi (test card).",
            })

        elif card_number == '4000000000009995':
            payment.mark_failed(reason='Insufficient funds', gateway_data={'mock': True})
            return render(request, self.template_name, {
                'payment': payment, 'error': "Kartada mablag' yetishmaydi (test card).",
            })

        else:
            import random
            if random.random() < 0.8:
                payment.card_brand = brand
                payment.card_last4 = last4
                payment.mark_paid(transaction_id=f'mock-{payment.id}', gateway_data={'mock': True, 'last4': last4})
                messages.success(request, "To'lov muvaffaqiyatli! (Mock mode)")
                return redirect('payments:success', booking_id=payment.booking.id)
            else:
                payment.mark_failed(reason='Random mock failure', gateway_data={'mock': True})
                return render(request, self.template_name, {
                    'payment': payment, 'error': "Tasodifiy xato. 4242 4242 4242 4242 ishlatib ko'ring.",
                })


class PaymentReturnView(LoginRequiredMixin, View):
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        if payment.status == 'paid':
            return redirect('payments:success', booking_id=payment.booking.id)
        elif payment.status in ('failed', 'cancelled'):
            return redirect('payments:failed', booking_id=payment.booking.id)
        return render(request, 'payments/payment_pending.html', {'payment': payment})


class PaymentStatusAPIView(LoginRequiredMixin, View):
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'not_found'}, status=404)
        return JsonResponse({
            'status': payment.status,
            'method': payment.method,
            'amount_uzs': payment.amount_uzs_formatted,
            'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
        })


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = get_object_or_404(Booking, pk=kwargs['booking_id'], user=self.request.user)
        return context


class PaymentFailedView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/payment_failed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = get_object_or_404(Booking, pk=kwargs['booking_id'], user=self.request.user)
        return context


# Webhooks — mock rejimda ishlamaydi
@method_decorator(csrf_exempt, name='dispatch')
class ClickWebhookView(View):
    def post(self, request):
        if is_mock_mode():
            return JsonResponse({'error': 'mock_mode'}, status=503)
        from .gateways.click import ClickService
        data = request.POST.dict()
        action = int(data.get('action', -1))
        try:
            if action == 0:
                response = ClickService.handle_prepare(data)
            elif action == 1:
                response = ClickService.handle_complete(data)
            else:
                response = {'error': -3, 'error_note': 'Action not found'}
        except Exception as e:
            logger.exception("Click webhook error")
            response = {'error': -8, 'error_note': str(e)}
        return JsonResponse(response)


@method_decorator(csrf_exempt, name='dispatch')
class PaymeWebhookView(View):
    def post(self, request):
        if is_mock_mode():
            return JsonResponse({'error': {'code': -32400, 'message': 'mock_mode'}}, status=503)
        from .gateways.payme import PaymeService, PaymeError
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not PaymeService.verify_auth(auth):
            return JsonResponse({'jsonrpc': '2.0', 'error': {'code': -32504, 'message': {'en': 'Unauthorized'}}, 'id': None})
        try:
            body = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'jsonrpc': '2.0', 'error': {'code': -32700, 'message': {'en': 'Parse error'}}, 'id': None})

        method = body.get('method', '')
        params = body.get('params', {})
        rpc_id = body.get('id')

        method_map = {
            'CheckPerformTransaction': PaymeService.check_perform_transaction,
            'CreateTransaction': PaymeService.create_transaction,
            'PerformTransaction': PaymeService.perform_transaction,
            'CancelTransaction': PaymeService.cancel_transaction,
            'CheckTransaction': PaymeService.check_transaction,
        }
        handler = method_map.get(method)
        if not handler:
            return JsonResponse({'jsonrpc': '2.0', 'error': {'code': -32601, 'message': {'en': 'Method not found'}}, 'id': rpc_id})

        try:
            result = handler(params)
            return JsonResponse({'jsonrpc': '2.0', 'result': result, 'id': rpc_id})
        except PaymeError as e:
            return JsonResponse({'jsonrpc': '2.0', 'error': {'code': e.code, 'message': {'en': e.message}}, 'id': rpc_id})
        except Exception as e:
            logger.exception("Payme webhook error")
            return JsonResponse({'jsonrpc': '2.0', 'error': {'code': -32400, 'message': {'en': str(e)}}, 'id': rpc_id})