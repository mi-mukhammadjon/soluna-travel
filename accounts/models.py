from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('admin', _('Администратор')),
    ]
    phone = models.CharField(_('Номер телефона'), max_length=20, blank=True)
    avatar = models.ImageField(_('Аватар'), upload_to='avatars/', blank=True, null=True)
    role = models.CharField(_('Роль'), max_length=10, choices=ROLE_CHOICES, default='user')
    preferred_language = models.CharField(
        _('Предпочитаемый язык'),
        max_length=10,
        choices=settings.LANGUAGES,  # <- Settings dan olinadi
        default=settings.LANGUAGE_CODE
    )
    
    # is_verified va email_verification_token OLIB TASHLANDI. 
    # Buni allauth o'zining EmailAddress modelida saqlaydi!

    created_at = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Все пользователи')

    def __str__(self):
        return self.email or self.username

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.username


class SiteSettings(models.Model):
    site_name = models.CharField('Sayt nomi', max_length=100, default='SoLuna')
    site_tagline = models.CharField('Slogan', max_length=200, default='Your Gateway to Extraordinary Adventures')

    phone_1 = models.CharField('Telefon 1', max_length=20, default='+998 99 895 35 36')
    phone_2 = models.CharField('Telefon 2', max_length=20, blank=True)
    email_1 = models.EmailField('Email 1', default='solunadmc@gmail.com')
    email_2 = models.EmailField('Email 2', blank=True)

    director = models.CharField('Direktor (F.I.SH.)', max_length=120, blank=True, default='Axatova Oygul')
    address = models.CharField('Manzil', max_length=300, default='Tashkent, Uzbekistan')
    map_coords = models.CharField(
        'Xarita koordinatalari (lat,lng)', max_length=60, blank=True,
        default='41.24087217365655,69.31545925558227',
        help_text="Google Maps'dan lat,lng — masalan: 41.240872,69.315459",
    )
    work_hours = models.CharField('Ish vaqti', max_length=100, default='8:00 – 18:00, Mon – Sat')

    instagram = models.URLField('Instagram', blank=True, default='https://instagram.com/Oygul.axatova')
    telegram = models.URLField('Telegram', blank=True, default='https://t.me/soluna_uz')
    whatsapp = models.URLField('WhatsApp', blank=True, default='https://wa.me/998950666233')
    facebook = models.URLField('Facebook', blank=True)

    promo_text = models.CharField('Promo matn', max_length=200, default='Unlock the Magic of Travel with SoLuna')
    promo_cta_text = models.CharField('Promo tugma matni', max_length=50, default='Explore Now')
    promo_cta_url = models.URLField('Promo tugma URL', blank=True, default='/tours/')

    class Meta:
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj