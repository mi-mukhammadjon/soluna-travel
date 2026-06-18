"""
Click to'lov tizimi integratsiyasi.
Docs: https://docs.click.uz
"""
import hashlib
from django.conf import settings


CLICK_SERVICE_ID = settings.CLICK_SERVICE_ID
CLICK_MERCHANT_ID = settings.CLICK_MERCHANT_ID
CLICK_SECRET_KEY = settings.CLICK_SECRET_KEY


def generate_click_url(booking, payment):
    """Click to'lov sahifasiga yo'naltirish URL yaratish"""
    amount = int(payment.amount)  # tiyin emas, so'm
    return_url = f"{settings.SITE_URL}/payments/click/return/"

    url = (
        f"https://my.click.uz/services/pay"
        f"?service_id={CLICK_SERVICE_ID}"
        f"&merchant_id={CLICK_MERCHANT_ID}"
        f"&amount={amount}"
        f"&transaction_param={payment.transaction_id}"
        f"&return_url={return_url}"
    )
    return url


def verify_click_signature(data):
    """Click webhook imzosini tekshirish"""
    sign_string = (
        f"{data.get('click_trans_id')}"
        f"{CLICK_SERVICE_ID}"
        f"{CLICK_SECRET_KEY}"
        f"{data.get('merchant_trans_id')}"
        f"{data.get('amount')}"
        f"{data.get('action')}"
        f"{data.get('sign_time')}"
    )
    expected = hashlib.md5(sign_string.encode()).hexdigest()
    return expected == data.get('sign_string')