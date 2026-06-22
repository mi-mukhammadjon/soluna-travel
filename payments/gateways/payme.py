# payments/gateways/payme.py
"""
Payme Merchant API integratsiyasi (JSON-RPC 2.0).

Payme metodlari:
- CheckPerformTransaction — tranzaksiya boshlanishidan oldin tekshirish
- CreateTransaction — tranzaksiya yaratish
- PerformTransaction — to'lovni tasdiqlash (pul kelgan)
- CancelTransaction — bekor qilish / refund
- CheckTransaction — holat
- GetStatement — outlet'lar uchun

Hujjat: https://developer.help.paycom.uz/
"""
import base64
import time
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import datetime


# Payme error codes
class PaymeErrorCode:
    INTERNAL_ERROR = -32400
    METHOD_NOT_FOUND = -32601
    INVALID_AMOUNT = -31001
    TRANSACTION_NOT_FOUND = -31003
    UNABLE_TO_CANCEL = -31007
    PENDING_PAYMENT = -31050
    ORDER_NOT_FOUND = -31050
    UNABLE_TO_PERFORM = -31008
    INVALID_AUTHORIZATION = -32504


class PaymeTransactionState:
    CREATED = 1
    COMPLETED = 2
    CANCELLED = -1
    CANCELLED_AFTER_COMPLETE = -2


class PaymeError(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class PaymeService:
    """Payme to'lov xizmati"""

    @staticmethod
    def _get_setting(key):
        val = getattr(settings, key, None)
        if not val:
            raise Exception(f"settings.{key} sozlanmagan")
        return val

    @classmethod
    def get_merchant_id(cls):
        return cls._get_setting('PAYME_MERCHANT_ID')

    @classmethod
    def get_secret_key(cls):
        return cls._get_setting('PAYME_SECRET_KEY')

    @classmethod
    def get_test_key(cls):
        return getattr(settings, 'PAYME_TEST_KEY', None)

    @classmethod
    def verify_auth(cls, auth_header):
        """Basic Auth header tekshirish: Paycom:<KEY>"""
        if not auth_header or not auth_header.startswith('Basic '):
            return False

        try:
            decoded = base64.b64decode(auth_header[6:]).decode()
            user, key = decoded.split(':', 1)
            if user != 'Paycom':
                return False
            secret = cls.get_secret_key()
            return key == secret
        except Exception:
            return False

    @classmethod
    def generate_payment_url(cls, payment, return_url=None):
        """
        Payme'ga yo'naltirish URL'i.
        Payload base64'da bo'ladi.
        """
        merchant_id = cls.get_merchant_id()
        amount_tiyin = payment.amount_uzs  # Tiyinda

        params = {
            'm': merchant_id,
            'ac.payment_id': str(payment.id),
            'a': amount_tiyin,
        }
        if return_url:
            params['c'] = return_url
        params['l'] = 'uz'  # til

        # ;-bilan birlashtirish
        payload = ';'.join(f"{k}={v}" for k, v in params.items())
        encoded = base64.b64encode(payload.encode()).decode()

        return f"https://checkout.paycom.uz/{encoded}"

    # ── JSON-RPC method handlers ────────────────────────────

    @classmethod
    def check_perform_transaction(cls, params):
        """
        CheckPerformTransaction
        Payme tranzaksiya boshlamoqchi — biz tekshiramiz.
        """
        from payments.models import Payment

        amount = params.get('amount')  # Tiyinda
        account = params.get('account', {})
        payment_id = account.get('payment_id')

        try:
            payment = Payment.objects.get(id=payment_id)
        except (Payment.DoesNotExist, ValueError):
            raise PaymeError(PaymeErrorCode.ORDER_NOT_FOUND, "Order not found", {'uz': "Buyurtma topilmadi"})

        if payment.amount_uzs != amount:
            raise PaymeError(PaymeErrorCode.INVALID_AMOUNT, "Invalid amount")

        if payment.status == 'paid':
            raise PaymeError(PaymeErrorCode.UNABLE_TO_PERFORM, "Already paid")

        return {'allow': True}

    @classmethod
    def create_transaction(cls, params):
        """
        CreateTransaction
        Payme tranzaksiya yaratmoqchi.
        """
        from payments.models import Payment

        transaction_id = params.get('id')
        timestamp = params.get('time')
        amount = params.get('amount')
        account = params.get('account', {})
        payment_id = account.get('payment_id')

        try:
            payment = Payment.objects.get(id=payment_id)
        except (Payment.DoesNotExist, ValueError):
            raise PaymeError(PaymeErrorCode.ORDER_NOT_FOUND, "Order not found")

        if payment.amount_uzs != amount:
            raise PaymeError(PaymeErrorCode.INVALID_AMOUNT, "Invalid amount")

        if payment.status == 'paid':
            raise PaymeError(PaymeErrorCode.UNABLE_TO_PERFORM, "Already paid")

        # Tranzaksiya yaratilgan
        if payment.gateway_transaction_id and payment.gateway_transaction_id != transaction_id:
            raise PaymeError(PaymeErrorCode.PENDING_PAYMENT, "Another transaction pending")

        payment.gateway_transaction_id = transaction_id
        payment.status = 'processing'
        payment.gateway_response = {**payment.gateway_response, 'create_time': timestamp}
        payment.save()

        return {
            'create_time': timestamp,
            'transaction': str(payment.id),
            'state': PaymeTransactionState.CREATED,
        }

    @classmethod
    def perform_transaction(cls, params):
        """
        PerformTransaction — pul keldi, booking confirm qilamiz.
        """
        from payments.models import Payment

        transaction_id = params.get('id')

        try:
            payment = Payment.objects.get(gateway_transaction_id=transaction_id)
        except Payment.DoesNotExist:
            raise PaymeError(PaymeErrorCode.TRANSACTION_NOT_FOUND, "Transaction not found")

        if payment.status == 'paid':
            # Idempotent — javobni qaytaramiz
            perform_time = int(payment.paid_at.timestamp() * 1000) if payment.paid_at else int(time.time() * 1000)
            return {
                'perform_time': perform_time,
                'transaction': str(payment.id),
                'state': PaymeTransactionState.COMPLETED,
            }

        if payment.status in ('cancelled', 'refunded', 'failed'):
            raise PaymeError(PaymeErrorCode.UNABLE_TO_PERFORM, "Cannot perform")

        # Muvaffaqiyatli
        payment.mark_paid(transaction_id=transaction_id, gateway_data={'perform_time': int(time.time() * 1000)})

        return {
            'perform_time': int(payment.paid_at.timestamp() * 1000),
            'transaction': str(payment.id),
            'state': PaymeTransactionState.COMPLETED,
        }

    @classmethod
    def cancel_transaction(cls, params):
        """CancelTransaction — bekor qilish"""
        from payments.models import Payment

        transaction_id = params.get('id')
        reason = params.get('reason')

        try:
            payment = Payment.objects.get(gateway_transaction_id=transaction_id)
        except Payment.DoesNotExist:
            raise PaymeError(PaymeErrorCode.TRANSACTION_NOT_FOUND, "Transaction not found")

        cancel_time = int(time.time() * 1000)
        was_paid = payment.status == 'paid'

        payment.mark_cancelled()
        payment.gateway_response = {
            **payment.gateway_response,
            'cancel_time': cancel_time,
            'cancel_reason': reason,
        }
        payment.save()

        # Booking holatini qaytarish
        if was_paid:
            payment.booking.status = 'cancelled'
            payment.booking.save()
            state = PaymeTransactionState.CANCELLED_AFTER_COMPLETE
        else:
            state = PaymeTransactionState.CANCELLED

        return {
            'cancel_time': cancel_time,
            'transaction': str(payment.id),
            'state': state,
        }

    @classmethod
    def check_transaction(cls, params):
        """CheckTransaction — holatni so'rash"""
        from payments.models import Payment

        transaction_id = params.get('id')
        try:
            payment = Payment.objects.get(gateway_transaction_id=transaction_id)
        except Payment.DoesNotExist:
            raise PaymeError(PaymeErrorCode.TRANSACTION_NOT_FOUND, "Transaction not found")

        state_map = {
            'created': PaymeTransactionState.CREATED,
            'processing': PaymeTransactionState.CREATED,
            'paid': PaymeTransactionState.COMPLETED,
            'cancelled': PaymeTransactionState.CANCELLED,
            'failed': PaymeTransactionState.CANCELLED,
        }
        state = state_map.get(payment.status, PaymeTransactionState.CREATED)

        gw = payment.gateway_response or {}
        create_time = gw.get('create_time', 0)
        perform_time = int(payment.paid_at.timestamp() * 1000) if payment.paid_at else 0
        cancel_time = gw.get('cancel_time', 0)

        return {
            'create_time': create_time,
            'perform_time': perform_time,
            'cancel_time': cancel_time,
            'transaction': str(payment.id),
            'state': state,
            'reason': gw.get('cancel_reason'),
        }