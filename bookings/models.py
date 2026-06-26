from django.db import models
from django.conf import settings
from django.utils import timezone
from tours.models import Tour
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name='bookings')
    booking_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    # Sayohat ma'lumotlari
    travel_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)

    # Narx
    price_per_person = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')

    # Qo'shimcha
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'

    def __str__(self):
        return f"{self.booking_number} — {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = 'BK' + uuid.uuid4().hex[:8].upper()
        if self.price_per_person is None:
            self.price_per_person = self.tour.price
        if self.total_price is None:
            self.total_price = (
                self.tour.discounted_price * self.num_adults
                + self.tour.child_price * self.num_children
            )
        super().save(*args, **kwargs)

    @property
    def total_persons(self):
        return self.num_adults + self.num_children

    @property
    def adults_subtotal(self):
        """Kattalar uchun jami: kishi narxi × kattalar soni."""
        return self.price_per_person * self.num_adults

    @property
    def children_subtotal(self):
        """Bolalar uchun jami (saqlangan total bilan mos: total − kattalar jami)."""
        return self.total_price - self.adults_subtotal

    @property
    def child_price_per_person(self):
        """Bitta bola uchun narx."""
        if self.num_children:
            return self.children_subtotal / self.num_children
        return self.tour.child_price

    @property
    def can_cancel(self):
        """Sayohat sanasidan 3 kun oldin bekor qilish mumkin"""
        if self.status in ('cancelled', 'completed'):
            return False
        days_until = (self.travel_date - timezone.now().date()).days
        return days_until >= 3