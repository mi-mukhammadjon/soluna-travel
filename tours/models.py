from decimal import Decimal
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from regions.models import Region, Attraction
from django.core.validators import FileExtensionValidator, MaxValueValidator

# Tur "yangi" deb hisoblanadigan davr (kun)
NEW_TOUR_DAYS = 60


class TourCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(
        upload_to='categories/images/', 
        null=True, 
        blank=True,
        # Kategoriya uchun barcha rasm formatlariga ruxsat beramiz
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'svg'])]
    )

    class Meta:
        verbose_name = 'Категория тура'
        verbose_name_plural = 'Категории туров'

    def __str__(self):
        return self.name
    
    @property
    def tour_count(self):
        # Agar View ichida annotate bilan (masalan: Count('tour_set')) hisoblangan bo'lsa
        if hasattr(self, '_tour_count'):
            return self._tour_count
        # Aks holda, sekinroq, dinamik bazaga murojaat qilib hisoblaydi
        return self.tour.filter(is_active=True).count()

    @tour_count.setter
    def tour_count(self, value):
        self._tour_count = value


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
    cover_image = models.ImageField(
        upload_to='tours/covers/', 
        blank=True, 
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_uzs = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    child_price_percent = models.PositiveSmallIntegerField(
        default=50,
        validators=[MaxValueValidator(100)],
        help_text="Bola narxi — katta odam narxining foizi (0–100). "
                  "Masalan 50 = yarim narx, 0 = bepul, 100 = to'liq narx."
    )
    duration_days = models.PositiveIntegerField()
    max_group_size = models.PositiveIntegerField(default=15)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    includes = models.TextField(blank=True)
    excludes = models.TextField(blank=True)
    itinerary = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(
        default=False,
        help_text="Tavsiya etilgan turlar ro'yxatida ko'rsatiladi."
    )

    # ── Maxsus taklif / chegirma ──
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(90)],
        help_text="Chegirma foizi (0–90). 0 bo'lsa chegirma yo'q."
    )
    discount_label = models.CharField(
        max_length=60, blank=True,
        help_text="Masalan: 'Yozgi aksiya', 'Early Bird'. Bo'sh bo'lsa 'Sale' ko'rsatiladi."
    )
    discount_until = models.DateField(
        null=True, blank=True,
        help_text="Chegirma amal qilish muddati (ixtiyoriy). Bo'sh bo'lsa muddatsiz."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Тур'
        verbose_name_plural = 'Туры'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Tour.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    # --- MAXSUS TAKLIF / CHEGIRMA ---
    @property
    def has_discount(self):
        """Faol chegirma bormi? (foiz > 0 va muddati o'tmagan)"""
        if not self.discount_percent or self.discount_percent <= 0:
            return False
        if self.discount_until and self.discount_until < timezone.now().date():
            return False
        return True

    @property
    def discounted_price(self):
        """Chegirma qo'llangan yakuniy narx (faol bo'lsa), aks holda asl narx."""
        if not self.has_discount:
            return self.price
        factor = (Decimal(100) - Decimal(self.discount_percent)) / Decimal(100)
        return (self.price * factor).quantize(Decimal('0.01'))

    @property
    def discount_amount(self):
        """Chegirma summasi (asl narx − chegirmali narx)."""
        return self.price - self.discounted_price

    @property
    def child_price(self):
        """Bitta bola uchun narx — chegirmali narxning child_price_percent foizi."""
        factor = Decimal(self.child_price_percent) / Decimal(100)
        return (self.discounted_price * factor).quantize(Decimal('0.01'))

    @property
    def is_new(self):
        """Tur so'nggi NEW_TOUR_DAYS kun ichida yaratilganmi?"""
        if not self.created_at:
            return False
        return (timezone.now() - self.created_at).days <= NEW_TOUR_DAYS

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
    image = models.ImageField(
        upload_to='tours/gallery/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.tour.title} - {self.order}"

class ItineraryDay(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='days')
    day = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    class Meta:
        ordering = ['day']


class CompanyStatistic(models.Model):
    number = models.CharField(max_length=20, help_text="Masalan: 45+, 29K, 168K")
    label = models.CharField(max_length=100, help_text="Masalan: Global Branches")
    order = models.PositiveIntegerField(default=0, help_text="Saytda chiqish ketma-ketligi")

    class Meta:
        ordering = ['order']
        verbose_name = 'Статистика компании'
        verbose_name_plural = 'Статистика компании'

    def __str__(self):
        return f"{self.number} - {self.label}"


class CompanyAdvantage(models.Model):
    COLOR_CHOICES = [
        ('orange', 'Orange (To''q sariq)'),
        ('blue', 'Blue (Ko''k)'),
        ('teal', 'Teal (Yashil)'),
        ('purple', 'Purple (Siyohrang)'),
    ]
    
    icon = models.CharField(max_length=50, help_text="Tabler icon klassi (masalan: ti-camera, ti-thumb-up)")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='orange')
    title = models.TextField()
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Преимущество компании'
        verbose_name_plural = 'Преимущества компании'

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'tour']
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"{self.user} — {self.tour}"