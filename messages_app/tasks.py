from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import requests


def send_sms_eskiz(phone, message):
    """Eskiz.uz orqali SMS yuborish"""
    try:
        # Token olish
        auth = requests.post(
            'https://notify.eskiz.uz/api/auth/login',
            data={'email': settings.ESKIZ_EMAIL, 'password': settings.ESKIZ_PASSWORD},
            timeout=10
        )
        token = auth.json().get('data', {}).get('token')
        if not token:
            return False

        # SMS yuborish
        resp = requests.post(
            'https://notify.eskiz.uz/api/message/sms/send',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'mobile_phone': phone.replace('+', '').replace(' ', ''),
                'message': message,
                'from': '4546',
            },
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False


@shared_task
def notify_admin_new_message(message_id):
    """Admin ga yangi xabar kelganda email yuborish"""
    from .models import ContactMessage
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        msg = ContactMessage.objects.get(pk=message_id)
        admins = User.objects.filter(is_staff=True, email__isnull=False).exclude(email='')

        subject = f"Yangi xabar: {msg.subject}"
        
        # Telefon raqamini oldindan tayyorlab olamiz (f-stringdan tashqarida)
        phone_text = msg.phone or "Ko'rsatilmagan"
        
        body = (
            f"Kimdan: {msg.name} ({msg.email})\n"
            f"Telefon: {phone_text}\n"  # <--- Endi bu yerda hech qanday muammo bo'lmaydi
            f"Mavzu: {msg.subject}\n\n"
            f"Xabar:\n{msg.body}"
        )

        for admin in admins:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True,
            )
    except ContactMessage.DoesNotExist:
        pass


@shared_task
def send_reply_email(message_id):
    """Foydalanuvchiga javob emaili yuborish"""
    from .models import ContactMessage
    try:
        msg = ContactMessage.objects.get(pk=message_id)
        subject = f"Xabringizga javob: {msg.subject}"
        body = (
            f"Hurmatli {msg.name},\n\n"
            f"Xabringizga javob:\n\n"
            f"{msg.reply_text}\n\n"
            f"Hurmat bilan,\n"
            f"TourUzbekistan jamoasi"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[msg.email],
            fail_silently=True,
        )

        # SMS ham yuborish (telefon bo'lsa)
        if msg.phone:
            sms_text = f"TourUzbekistan: Xabringizga javob berildi. Email: {msg.email}"
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
            f"TourUzbekistan: Broningiz tasdiqlandi! "
            f"Raqam: {booking.booking_number}, "
            f"Tur: {booking.tour.title[:20]}, "
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