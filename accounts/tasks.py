from celery import shared_task
from django.utils.translation import gettext_lazy as _
from config.emails import send_branded_email


@shared_task
def send_welcome_email(user_id):
    from .models import User
    try:
        user = User.objects.get(pk=user_id)
        if not user.email:
            return
        send_branded_email(
            to=user.email,
            subject=_("Welcome to SoLuna Travel!"),
            template="emails/welcome.html",
            context={"name": user.get_full_name() or user.username},
            lang=getattr(user, "preferred_language", None),
        )
    except User.DoesNotExist:
        pass
