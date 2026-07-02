"""Brendli, ko'p tilli HTML email yuborish yordamchisi (SoLuna)."""
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _site():
    try:
        from accounts.models import SiteSettings
        return SiteSettings.load()
    except Exception:
        return None


def _site_url():
    url = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    if not url or 'localhost' in url or '127.0.0.1' in url:
        url = 'https://solunatravel.uz'
    return url


def send_branded_email(to, subject, template, context=None, lang=None):
    """Elegant HTML (emails/base_email.html asosida) + matnli nusxa.
    `lang` — foydalanuvchi tili (masalan user.preferred_language); bo'lmasa standart til."""
    if not to:
        return False
    recipients = [to] if isinstance(to, str) else list(to)
    site = _site()
    base_url = _site_url()
    brand = site.site_name if (site and site.site_name) else 'SoLuna Travel'
    logo_path = site.logo_url if site else '/static/img/site-icon.svg'
    logo_url = logo_path if str(logo_path).startswith('http') else base_url + logo_path
    ctx = {'brand': brand, 'site_url': base_url, 'logo_url': logo_url}
    ctx.update(context or {})
    try:
        with translation.override(lang or settings.LANGUAGE_CODE):
            subj = str(subject)  # gettext_lazy shu yerda aktiv tilda hal bo'ladi
            html = render_to_string(template, ctx)
        text = strip_tags(html)
        msg = EmailMultiAlternatives(subj, text, settings.DEFAULT_FROM_EMAIL, recipients)
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.warning('send_branded_email xatosi (%s): %s', template, e)
        return False
