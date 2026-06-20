# payments/gateways/click.py
"""
Click.uz SHOP API integratsiyasi.

Click ikki bosqichda ishlaydi:
1. PREPARE — Click bizdan tasdiq so'raydi (booking topiladimi, narx to'g'rimi)
2. COMPLETE — Click pul yechilgani haqida xabar beradi

Hujjat: https://docs.click.uz/en/click-api/
"""
import hashlib
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode


class ClickError(Exception):
    pass


# Click javob statuslari
class ClickStatus:
    SUCCESS = 0
    ERROR_SIGN_CHECK = -1
    ERROR_INCORRECT_AMOUNT = -2
    ERROR_ACTION_NOT_FOUND = -3
    ERROR_ALREADY_PAID = -4
    ERROR_USER_NOT_FOUND = -5
    ERROR_TRANSACTION_NOT_FOUND = -6
    ERROR_FAILED_TO_UPDATE_USER = -7
    ERROR_PAYMENT_FAILED = -8
    ERROR_TRANSACTION_CANCELLED = -9


# Click action
class ClickAction:
    PREPARE = 0
    COMPLETE = 1


class ClickService:
    """Click to'lov xizmati"""

    @staticmethod
    def _get_setting(key):
        val = getattr(settings, key, None)
        if not val:
            raise ClickError(f"settings.{key} sozlanmagan")
        return val

    @classmethod
    def get_merchant_id(cls):
        return cls._get_setting('CLICK_MERCHANT_ID')

    @classmethod
    def get_service_id(cls):
        return cls._get_setting('CLICK_SERVICE_ID')

    @classmethod
    def get_secret_key(cls):
        return cls._get_setting('CLICK_SECRET_KEY')

    @classmethod
    def generate_payment_url(cls, payment, return_url=None):
        """
        Foydalanuvchini Click sahifasiga olib boruvchi URL.
        amount — UZS so'mda (Click UZS qabul qiladi, tiyin emas)
        """
        merchant_id = cls.get_merchant_id()
        service_id = cls.get_service_id()
        amount_soms = payment.amount_uzs / 100  # tiyin → so'm

        params = {
            'service_id': service_id,
            'merchant_id': merchant_id,
            'amount': f"{amount_soms:.2f}",
            'transaction_param': str(payment.id),
        }
        if return_url:
            params['return_url'] = return_url

        return f"https://my.click.uz/services/pay?{urlencode(params)}"

    @classmethod
    def verify_signature(cls, data, expected_action):
        """
        Click signature verification.
        
        PREPARE uchun:
        md5(click_trans_id + service_id + SECRET + merchant_trans_id + amount + action + sign_time)
        
        COMPLETE uchun:
        md5(click_trans_id + service_id + SECRET + merchant_trans_id + merchant_prepare_id + amount + action + sign_time)
        """
        secret = cls.get_secret_key()

        click_trans_id = data.get('click_trans_id', '')
        service_id = data.get('service_id', '')
        merchant_trans_id = data.get('merchant_trans_id', '')
        amount = data.get('amount', '')
        action = data.get('action', '')
        sign_time = data.get('sign_time', '')
        provided_sign = data.get('sign_string', '')

        if int(action) == ClickAction.PREPARE:
            sign_str = f"{click_trans_id}{service_id}{secret}{merchant_trans_id}{amount}{action}{sign_time}"
        else:  # COMPLETE
            merchant_prepare_id = data.get('merchant_prepare_id', '')
            sign_str = f"{click_trans_id}{service_id}{secret}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{sign_time}"

        expected = hashlib.md5(sign_str.encode()).hexdigest()
        return expected == provided_sign

    @classmethod
    def handle_prepare(cls, data):
        """
        Click PREPARE so'rovi.
        Tekshiramiz: Payment mavjudmi? Narx to'g'rimi? Holati to'g'rimi?
        """
        from payments.models import Payment

        # Signature
        if not cls.verify_signature(data, ClickAction.PREPARE):
            return {
                'error': ClickStatus.ERROR_SIGN_CHECK,
                'error_note': 'Invalid signature',
            }

        payment_id = data.get('merchant_trans_id')
        amount = Decimal(str(data.get('amount', '0')))

        try:
            payment = Payment.objects.get(id=payment_id)
        except (Payment.DoesNotExist, ValueError):
            return {
                'error': ClickStatus.ERROR_USER_NOT_FOUND,
                'error_note': 'Payment not found',
            }

        if payment.status == 'paid':
            return {
                'error': ClickStatus.ERROR_ALREADY_PAID,
                'error_note': 'Already paid',
            }

        if payment.status in ('cancelled', 'refunded'):
            return {
                'error': ClickStatus.ERROR_TRANSACTION_CANCELLED,
                'error_note': 'Cancelled',
            }

        # Click amount soms, biz tiyinda saqlaymiz
        expected_soms = payment.amount_uzs / 100
        if abs(float(amount) - expected_soms) > 0.01:
            return {
                'error': ClickStatus.ERROR_INCORRECT_AMOUNT,
                'error_note': f'Incorrect amount. Expected: {expected_soms}',
            }

        # PREPARE muvaffaqiyatli — pending qilamiz
        payment.status = 'processing'
        payment.gateway_transaction_id = str(data.get('click_trans_id', ''))
        payment.save()

        return {
            'click_trans_id': data.get('click_trans_id'),
            'merchant_trans_id': payment_id,
            'merchant_prepare_id': str(payment.id),  # Bizning yana bir ID
            'error': ClickStatus.SUCCESS,
            'error_note': 'Success',
        }

    @classmethod
    def handle_complete(cls, data):
        """
        Click COMPLETE so'rovi — pul haqiqatdan ko'chirildi.
        """
        from payments.models import Payment

        if not cls.verify_signature(data, ClickAction.COMPLETE):
            return {
                'error': ClickStatus.ERROR_SIGN_CHECK,
                'error_note': 'Invalid signature',
            }

        payment_id = data.get('merchant_trans_id')
        error = int(data.get('error', 0))

        try:
            payment = Payment.objects.get(id=payment_id)
        except (Payment.DoesNotExist, ValueError):
            return {
                'error': ClickStatus.ERROR_USER_NOT_FOUND,
                'error_note': 'Payment not found',
            }

        if payment.status == 'paid':
            return {
                'error': ClickStatus.ERROR_ALREADY_PAID,
                'error_note': 'Already paid',
            }

        # Click xato bilan keldi (foydalanuvchi bekor qildi)
        if error < 0:
            payment.mark_failed(reason=data.get('error_note', 'Unknown'), gateway_data=data)
            return {
                'click_trans_id': data.get('click_trans_id'),
                'merchant_trans_id': payment_id,
                'merchant_confirm_id': str(payment.id),
                'error': ClickStatus.SUCCESS,
                'error_note': 'Marked as failed',
            }

        # MUVAFFAQIYAT — to'lovni paid qilamiz va booking confirmed
        payment.mark_paid(
            transaction_id=str(data.get('click_trans_id', '')),
            gateway_data=data,
        )

        return {
            'click_trans_id': data.get('click_trans_id'),
            'merchant_trans_id': payment_id,
            'merchant_confirm_id': str(payment.id),
            'error': ClickStatus.SUCCESS,
            'error_note': 'Success',
        }