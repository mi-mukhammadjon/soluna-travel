from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .tasks import send_welcome_email

@receiver(user_signed_up)
def send_welcome_email_on_signup(request, user, **kwargs):
    # Foydalanuvchi Allauth orqali muvaffaqiyatli ro'yxatdan o'tganda Celery ga vazifa beriladi
    send_welcome_email.delay(user.pk)