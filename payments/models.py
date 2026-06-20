# payments/models.py
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from bookings.models import Booking
import uuid


class Currency(models.Model):
    """Valyuta va kurslar (USD bazaviy)"""
    code = models.CharField(max_length=5, unique=True)  # USD, UZS, EUR
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5, default='')
    rate_to_usd = models.DecimalField(
        max_digits=14, decimal_places=4,
        help_text="1 USD = X currency. Masalan: UZS uchun 12700"
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    def __str__(self):
        return f"{self.code} ({self.rate_to_usd})"

    @classmethod
    def convert(cls, amount, from_code='USD', to_code='UZS'):
        """USD'dan boshqa valyutaga konversiya"""
        if from_code == to_code:
            return Decimal(str(amount))
        try:
            if from_code == 'USD':
                target = cls.objects.get(code=to_code, is_active=True)
                return Decimal(str(amount)) * target.rate_to_usd
            elif to_code == 'USD':
                source = cls.objects.get(code=from_code, is_active=True)
                return Decimal(str(amount)) / source.rate_to_usd
            else:
                # Cross-rate via USD
                source = cls.objects.get(code=from_code, is_active=True)
                target = cls.objects.get(code=to_code, is_active=True)
                usd_amount = Decimal(str(amount)) / source.rate_to_usd
                return usd_amount * target.rate_to_usd
        except cls.DoesNotExist:
            return Decimal(str(amount))


class Payment(models.Model):
    """To'lov tranzaksiyasi"""

    METHOD_CHOICES = [
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('card', 'Card (Manual)'),
        ('cash', 'Cash at office'),
        ('paypal', 'PayPal'),
    ]

    STATUS_CHOICES = [
        ('created', _('Created')),       # Yaratildi
        ('pending', _('Pending')),       # Gateway'ga yuborildi
        ('processing', _('Processing')), # Gateway tasdiqlamoqda
        ('paid', _('Paid')),             # Muvaffaqiyatli
        ('failed', _('Failed')),         # Xato
        ('cancelled', _('Cancelled')),   # Bekor qilingan
        ('refunded', _('Refunded')),     # Qaytarilgan
    ]

    # Ichki ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    # To'lov ma'lumotlari
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    # Pul (UZS tiyinda saqlanadi — Click/Payme talab qiladi)
    amount_uzs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2)
    exchange_rate = models.DecimalField(max_digits=14, decimal_places=4)

    # Gateway javobi
    gateway_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    # Card info (maskirovkalangan)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # visa, mastercard, uzcard, humo

    # Vaqt
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['gateway_transaction_id']),
        ]

    def __str__(self):
        return f"{self.method} — {self.amount_uzs/100:.0f} UZS ({self.status})"

    @property
    def amount_uzs_formatted(self):
        """1 234 567 so'm"""
        soms = self.amount_uzs / 100
        return f"{soms:,.0f}".replace(',', ' ')

    def mark_paid(self, transaction_id=None, gateway_data=None):
        """To'lov muvaffaqiyatli — booking'ni confirmed qilish"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        if transaction_id:
            self.gateway_transaction_id = transaction_id
        if gateway_data:
            self.gateway_response = gateway_data
        self.save()

        # Booking'ni confirmed qilish
        booking = self.booking
        booking.status = 'confirmed'
        booking.save()
        return True

    def mark_failed(self, reason='', gateway_data=None):
        self.status = 'failed'
        if gateway_data:
            self.gateway_response = {**self.gateway_response, 'error': reason, 'data': gateway_data}
        self.save()
        return True

    def mark_cancelled(self):
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()
        return True