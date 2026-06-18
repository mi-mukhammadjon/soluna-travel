from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


@shared_task
def send_verification_email(user_id):
    from .models import User
    try:
        user = User.objects.get(pk=user_id)
        verify_url = f"{settings.SITE_URL}{reverse('accounts:verify-email', kwargs={'token': user.email_verification_token})}"
        subject = "Emailingizni tasdiqlang — TourUzbekistan"
        message = f"""
Salom {user.get_full_name()},

Ro'yxatdan o'tganingiz uchun rahmat!

Emailingizni tasdiqlash uchun quyidagi havolani bosing:
{verify_url}

Agar siz ro'yxatdan o'tmagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring.

TourUzbekistan jamoasi
        """
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass


@shared_task
def send_welcome_email(user_id):
    from .models import User
    try:
        user = User.objects.get(pk=user_id)
        subject = "TourUzbekistan ga xush kelibsiz!"
        message = f"""
Salom {user.get_full_name()},

TourUzbekistan ga xush kelibsiz! 🎉

Endi siz:
- O'zbekistonning eng yaxshi turlarini ko'rishingiz
- Bronlar qilishingiz
- Izohlar qoldirishingiz mumkin.

Saytimizga tashrif buyuring: {settings.SITE_URL}

TourUzbekistan jamoasi
        """
        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except User.DoesNotExist:
        pass