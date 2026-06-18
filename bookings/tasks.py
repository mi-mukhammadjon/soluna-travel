from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.select_related('user', 'tour').get(pk=booking_id)
        name = booking.user.get_full_name() or booking.user.username
        subject = f"Bron tasdiqlandi — {booking.booking_number}"
        message = (
            f"Hurmatli {name},\n\n"
            f"Sizning broningiz tasdiqlandi!\n\n"
            f"Bron raqami: {booking.booking_number}\n"
            f"Tur: {booking.tour.title}\n"
            f"Sana: {booking.travel_date}\n"
            f"Kishilar: {booking.num_adults} katta, {booking.num_children} bola\n"
            f"Jami narx: ${booking.total_price}\n\n"
            f"Savollar bo'lsa, biz bilan bog'laning.\n\n"
            f"TourUzbekistan jamoasi"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
    except Booking.DoesNotExist:
        pass


@shared_task
def send_booking_cancellation_email(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.select_related('user', 'tour').get(pk=booking_id)
        name = booking.user.get_full_name() or booking.user.username
        reason = booking.cancellation_reason or "Ko'rsatilmagan"
        subject = f"Bron bekor qilindi — {booking.booking_number}"
        message = (
            f"Hurmatli {name},\n\n"
            f"Sizning broningiz bekor qilindi.\n\n"
            f"Bron raqami: {booking.booking_number}\n"
            f"Tur: {booking.tour.title}\n"
            f"Sana: {booking.travel_date}\n"
            f"Sabab: {reason}\n\n"
            f"TourUzbekistan jamoasi"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=True,
        )
    except Booking.DoesNotExist:
        pass