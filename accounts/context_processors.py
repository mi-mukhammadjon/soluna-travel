from django.conf import settings
from .models import SiteSettings


def site_settings(request):
    return {
        'site_settings': SiteSettings.load(),
        # SEO — qidiruv tizimlari tasdiqlash kodlari (.env dan)
        'google_site_verification': settings.GOOGLE_SITE_VERIFICATION,
        'yandex_verification': settings.YANDEX_VERIFICATION,
    }
