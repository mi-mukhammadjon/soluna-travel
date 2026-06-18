"""
Payme to'lov tizimi integratsiyasi.
Docs: https://developer.help.paycom.uz
"""
import base64
import hashlib
from django.conf import settings


PAYME_ID = settings.PAYME_ID
PAYME_KEY = settings.PAYME_KEY


def generate_payme_url(booking, payment):
    """Payme to'lov sahifasiga yo'naltirish URL yaratish"""
    amount_tiyin = int(payment.amount * 100)  # so'mni tiyinga o'girish

    params = f"m={PAYME_ID};ac.booking_id={booking.id};a={amount_tiyin}"
    encoded = base64.b64encode(params.encode()).decode()

    return f"https://checkout.paycom.uz/{encoded}"


def verify_payme_auth(auth_header):
    """Payme webhook autentifikatsiyasini tekshirish"""
    if not auth_header or not auth_header.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode()
        _, password = decoded.split(':', 1)
        return password == PAYME_KEY
    except Exception:
        return False


# Payme xato kodlari
PAYME_ERRORS = {
    -32700: "Parse error",
    -32600: "Invalid request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -31050: "Order not found",
    -31051: "Order already paid",
    -31052: "Amount mismatch",
    -31053: "Order cancelled",
}