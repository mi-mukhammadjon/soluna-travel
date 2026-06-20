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