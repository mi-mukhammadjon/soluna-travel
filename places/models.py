from django.db import models
from regions.models import Attraction


class NearbyPlace(models.Model):
    """2GIS yoki Google dan olingan yaqin atrofdagi joylar (kafe, hotel va h.k.)"""
    CATEGORY_CHOICES = [
        ('cafe', 'Kafe / Restoran'),
        ('hotel', 'Mehmonxona'),
        ('museum', 'Muzey'),
        ('pharmacy', 'Dorixona'),
        ('atm', 'ATM'),
        ('transport', 'Transport'),
        ('other', 'Boshqa'),
    ]

    attraction = models.ForeignKey(
        Attraction, on_delete=models.CASCADE,
        related_name='nearby_places', null=True, blank=True
    )
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    address = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    source = models.CharField(max_length=20, default='2gis')   # '2gis' yoki 'google'
    external_id = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Nearby Place'
        verbose_name_plural = 'Nearby Places'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"