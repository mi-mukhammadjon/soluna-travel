from django.db import models
from django.db.models import Avg  # <--- IMPORT QO'SHILDI (Property ishlashi uchun)
from django.utils.text import slugify
from regions.models import Region, Attraction


class TourCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Tour Category'
        verbose_name_plural = 'Tour Categories'

    def __str__(self):
        return self.name


class Tour(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(TourCategory, on_delete=models.SET_NULL, null=True, blank=True)
    regions = models.ManyToManyField(Region, related_name='tours')
    attractions = models.ManyToManyField(Attraction, related_name='tours', blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    cover_image = models.ImageField(upload_to='tours/covers/', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_uzs = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    duration_days = models.PositiveIntegerField()
    max_group_size = models.PositiveIntegerField(default=15)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    includes = models.TextField(blank=True)
    excludes = models.TextField(blank=True)
    itinerary = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Tour'
        verbose_name_plural = 'Tours'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # --- 1. AVG_RATING PROPERTY VA SETTER ---
    @property
    def avg_rating(self):
        if hasattr(self, '_avg_rating'):
            return self._avg_rating
        # Agar View ichida annotate ishlatilmagan bo'lsa, dinamik fallback hisoblash
        if hasattr(self, 'reviews'):
            return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        return 0

    @avg_rating.setter
    def avg_rating(self, value):
        """Django ORM annotate() qiymatini ob'ektga xavfsiz yuklashi uchun setter"""
        self._avg_rating = value

    # --- 2. REVIEW_COUNT PROPERTY VA SETTER ---
    @property
    def review_count(self):
        if hasattr(self, '_review_count'):
            return self._review_count
        # Agar View ichida Count() orqali yuklanmagan bo'lsa, dinamik hisoblash
        if hasattr(self, 'reviews'):
            return self.reviews.filter(is_approved=True).count()
        return 0

    @review_count.setter
    def review_count(self, value):
        """Django ORM Count() annotatsiyasini ob'ektga xavfsiz yuklashi uchun setter"""
        self._review_count = value


class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.tour.title} - {self.order}"