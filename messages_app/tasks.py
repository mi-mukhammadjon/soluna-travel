import logging
from celery import shared_task
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
import requests

logger = logging.getLogger(__name__)

ESKIZ_BASE = 'https://notify.eskiz.uz/api'
_TOKEN_CACHE_KEY = 'eskiz_token'


def _eskiz_token(force_refresh=False):
    """Eskiz tokenini Redis'da keshlaydi (~25 kun). Har SMS'da qayta login qilmaymiz."""
    if not (settings.ESKIZ_EMAIL and settings.ESKIZ_PASSWORD):
        return None
    if not force_refresh:
        tok = cache.get(_TOKEN_CACHE_KEY)
        if tok:
            return tok
    try:
        r = requests.post(
            f'{ESKIZ_BASE}/auth/login',
            data={'email': settings.ESKIZ_EMAIL, 'password': settings.ESKIZ_PASSWORD},
            timeout=10,
        )
        tok = (r.json().get('data') or {}).get('token')
        if tok:
            cache.set(_TOKEN_CACHE_KEY, tok, 60 * 60 * 24 * 25)
            return tok
        logger.warning('Eskiz auth: token qaytmadi [%s] %s', r.status_code, r.text[:300])
    except Exception as e:
        logger.warning('Eskiz auth xatosi: %s', e)
    return None


def _normalize_phone(phone):
    """Har qanday formatni Eskiz talab qiladigan 998XXXXXXXXX ga keltiradi."""
    d = ''.join(ch for ch in (phone or '') if ch.isdigit())
    if len(d) == 9:                       # 901234567
        d = '998' + d
    return d


def send_sms_eskiz(phone, message):
    """Eskiz.uz orqali SMS. Token keshlanadi, telefon normallashtiriladi, xatolar logga yoziladi.
    MUHIM: production'da SMS matni Eskiz kabinetida tasdiqlangan (moderatsiyadan o'tgan)
    bo'lishi va ESKIZ_FROM tasdiqlangan nick bo'lishi shart — aks holda haqiqiy raqamlarga yetmaydi."""
    mobile = _normalize_phone(phone)
    if len(mobile) != 12 or not mobile.startswith('998'):
        logger.warning("Eskiz: telefon formati noto'g'ri: %r", phone)
        return False

    token = _eskiz_token()
    if not token:
        logger.info("Eskiz: kredensiallar sozlanmagan yoki token yo'q — SMS o'tkazib yuborildi")
        return False

    for attempt in (1, 2):
        try:
            resp = requests.post(
                f'{ESKIZ_BASE}/message/sms/send',
                headers={'Authorization': f'Bearer {token}'},
                data={'mobile_phone': mobile, 'message': message,
                      'from': getattr(settings, 'ESKIZ_FROM', '4546')},
                timeout=15,
            )
            if resp.status_code == 401 and attempt == 1:
                token = _eskiz_token(force_refresh=True)   # token eskirgan — yangilaymiz
                if not token:
                    return False
                continue
            data = resp.json() if resp.content else {}
            status = str(data.get('status', '')).lower()
            ok = resp.status_code == 200 and (status in ('waiting', 'success') or 'id' in data)
            if not ok:
                logger.warning('Eskiz SMS muvaffaqiyatsiz [%s]: %s', resp.status_code, resp.text[:300])
            return ok
        except Exception as e:
            logger.warning('Eskiz SMS xatosi: %s', e)
            return False
    return False


def _brand():
    """SMS matnlari uchun sayt nomi (admin'dan)."""
    try:
        from accounts.models import SiteSettings
        return SiteSettings.load().site_name or 'SoLuna Travel'
    except Exception:
        return 'SoLuna Travel'


@shared_task
def notify_admin_new_message(message_id):
    """Admin ga yangi xabar kelganda email yuborish"""
    from django.core.mail import EmailMessage
    from .models import ContactMessage
    try:
        msg = ContactMessage.objects.get(pk=message_id)
    except ContactMessage.DoesNotExist:
        return

    # Qabul qiluvchi(lar) — admin paneldan boshqariladi (SiteSettings.notify_email)
    recipients = []
    try:
        from accounts.models import SiteSettings
        s = SiteSettings.load()
        for e in (s.notify_email, s.email_1, s.email_2):
            e = (e or '').strip()
            if e and e not in recipients:
                recipients.append(e)
    except Exception:
        pass
    if not recipients:  # zaxira — staff foydalanuvchilar
        from django.contrib.auth import get_user_model
        recipients = list(get_user_model().objects.filter(is_staff=True)
                          .exclude(email='').values_list('email', flat=True))
    if not recipients:
        return

    phone_text = msg.phone or "—"
    body = (
        f"Sayt orqali yangi xabar — solunatravel.uz\n"
        f"{'-' * 40}\n"
        f"Kimdan:  {msg.name} <{msg.email}>\n"
        f"Telefon: {phone_text}\n"
        f"Til:     {msg.language or '—'}\n"
        f"Vaqt:    {msg.created_at:%d.%m.%Y %H:%M}\n"
        f"Mavzu:   {msg.subject}\n"
        f"{'-' * 40}\n\n"
        f"{msg.body}\n"
    )
    # Reply-To = yuboruvchi: Gmail'da "Reply" bosilsa to'g'ridan-to'g'ri mijozga javob ketadi
    email = EmailMessage(
        subject=f"[SoLuna] {msg.subject}",
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[msg.email] if msg.email else None,
    )
    email.send(fail_silently=True)


@shared_task
def send_reply_email(message_id):
    """Foydalanuvchiga elegant, brendli javob emaili — o'z tilida."""
    from django.utils.translation import gettext_lazy as _
    from config.emails import send_branded_email
    from .models import ContactMessage
    try:
        msg = ContactMessage.objects.get(pk=message_id)
        subject = msg.reply_subject or (_("Re: %(subject)s") % {'subject': msg.subject})
        send_branded_email(
            to=msg.email,
            subject=subject,
            template="emails/reply.html",
            context={"name": msg.name, "reply": msg.reply_text, "original": msg.body},
            lang=msg.language or None,
        )

        # SMS ham yuborish (telefon bo'lsa)
        if msg.phone:
            sms_text = f"{_brand()}: so'rovingizga javob berdik. Batafsil ma'lumot emailingizga yuborildi."
            send_sms_eskiz(msg.phone, sms_text)

    except ContactMessage.DoesNotExist:
        pass


@shared_task
def send_booking_sms(booking_id):
    """Bron tasdiqlanganda SMS yuborish"""
    from bookings.models import Booking
    try:
        booking = Booking.objects.select_related('user', 'tour').get(pk=booking_id)
        phone = booking.user.phone
        if not phone:
            return

        text = (
            f"{_brand()}: broningiz tasdiqlandi! "
            f"Raqam: {booking.booking_number}, "
            f"Sana: {booking.travel_date}"
        )
        send_sms_eskiz(phone, text)
    except Booking.DoesNotExist:
        pass


@shared_task
def send_newsletter_email(newsletter_id):
    """Newsletter ni barcha faol obunachilarga yuborish"""
    from .models import Newsletter, NewsletterSubscriber
    try:
        newsletter = Newsletter.objects.get(pk=newsletter_id)
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)

        for subscriber in subscribers:
            send_mail(
                subject=newsletter.title,
                message=newsletter.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                fail_silently=True,
            )

        newsletter.status = 'sent'
        newsletter.sent_at = timezone.now()
        newsletter.save()
    except Newsletter.DoesNotExist:
        pass