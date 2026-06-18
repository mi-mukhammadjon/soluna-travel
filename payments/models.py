from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    PROVIDER_CHOICES = [
        ('click', 'Click'),
        ('payme', 'Payme'),
        ('cash', 'Cash'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('waiting', 'Waiting confirmation'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=5, default='UZS')
    transaction_id = models.CharField(max_length=200, blank=True)
    provider_transaction_id = models.CharField(max_length=200, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.booking.booking_number} — {self.provider} — {self.status}"