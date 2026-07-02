from celery import shared_task
from django.utils.translation import gettext_lazy as _
from config.emails import send_branded_email


@shared_task
def send_booking_confirmation_email(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.select_related('user', 'tour').get(pk=booking_id)
        if not booking.user.email:
            return
        travellers = _("%(adults)d adult(s), %(children)d child(ren)") % {
            'adults': booking.num_adults, 'children': booking.num_children}
        send_branded_email(
            to=booking.user.email,
            subject=_("Booking confirmed — %(num)s") % {'num': booking.booking_number},
            template="emails/booking_confirmed.html",
            context={
                "name": booking.user.get_full_name() or booking.user.username,
                "number": booking.booking_number,
                "tour": booking.tour.title,
                "date": booking.travel_date,
                "travellers": travellers,
                "total": f"${booking.total_price}",
            },
            lang=getattr(booking.user, "preferred_language", None),
        )
    except Booking.DoesNotExist:
        pass


@shared_task
def send_booking_cancellation_email(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.select_related('user', 'tour').get(pk=booking_id)
        if not booking.user.email:
            return
        reason = booking.cancellation_reason or str(_("Not specified"))
        send_branded_email(
            to=booking.user.email,
            subject=_("Booking cancelled — %(num)s") % {'num': booking.booking_number},
            template="emails/booking_cancelled.html",
            context={
                "name": booking.user.get_full_name() or booking.user.username,
                "number": booking.booking_number,
                "tour": booking.tour.title,
                "date": booking.travel_date,
                "reason": reason,
            },
            lang=getattr(booking.user, "preferred_language", None),
        )
    except Booking.DoesNotExist:
        pass
