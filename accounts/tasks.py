from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


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