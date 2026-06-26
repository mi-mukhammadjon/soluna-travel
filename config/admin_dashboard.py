# config/admin_dashboard.py
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET

from accounts.models import User
from bookings.models import Booking
from messages_app.models import ContactMessage
from tours.models import Tour
from payments.models import Payment
from reviews.models import Review
from regions.models import Region


@require_GET
@staff_member_required
def dashboard_stats(request):
    recent_bookings = (
        Booking.objects
        .select_related("user", "tour")
        .order_by("-created_at")[:5]
    )
    recent_messages = (
        ContactMessage.objects
        .filter(status="new")
        .order_by("-created_at")[:5]
    )
    recent_payments = (
        Payment.objects
        .select_related("user", "booking")
        .order_by("-created_at")[:5]
    )
    recent_reviews = (
        Review.objects
        .select_related("user", "tour")
        .order_by("-created_at")[:5]
    )
    regions = (
        Region.objects
        .filter(is_active=True)
        .order_by("name")[:6]
    )

    return JsonResponse({
        "kpi": {
            "bookings": Booking.objects.count(),
            "new_messages": ContactMessage.objects.filter(status="new").count(),
            "active_tours": Tour.objects.filter(is_active=True).count(),
            "users": User.objects.filter(is_staff=False).count(),
            "pending_bookings": Booking.objects.filter(status="pending").count(),
            "reviews": Review.objects.count(),
            "pending_reviews": Review.objects.filter(is_approved=False).count(),
        },
        "recent_bookings": [
            {
                "number": b.booking_number,
                "tour": str(b.tour),
                "user": b.user.get_full_name() or b.user.username,
                "status": b.status,
                "total": str(b.total_price),
                "url": reverse("admin:bookings_booking_change", args=[b.pk]),
            }
            for b in recent_bookings
        ],
        "recent_messages": [
            {
                "name": m.name,
                "subject": m.subject,
                "status": m.status,
                "url": reverse("admin:messages_app_contactmessage_change", args=[m.pk]),
            }
            for m in recent_messages
        ],
        "recent_payments": [
            {
                "method": p.get_method_display(),
                "amount": f"{int(p.amount_uzs/100):,} UZS",
                "user": p.user.get_full_name() or p.user.username,
                "booking": p.booking.booking_number if p.booking else "-",
                "status": p.status,
                "url": reverse("admin:payments_payment_change", args=[p.pk]),
            }
            for p in recent_payments
        ],
        "recent_reviews": [
            {
                "tour": str(r.tour),
                "user": r.user.get_full_name() or r.user.username,
                "stars": "★" * r.rating,
                "status": "confirmed" if r.is_approved else "pending",
                "url": reverse("admin:reviews_review_change", args=[r.pk]),
            }
            for r in recent_reviews
        ],
        "regions": [
            {
                "name": r.name,
                "tours": r.tours.count(),
                "url": reverse("admin:regions_region_change", args=[r.pk]),
            }
            for r in regions
        ],
    })


# ── config/urls.py ga qo'shing (admin.site.urls dan OLDIN): ──
#
# from config.admin_dashboard import dashboard_stats
#
# urlpatterns = i18n_patterns(
#     path("admin/dashboard-stats/", dashboard_stats, name="admin-dashboard-stats"),
#     path("admin/", admin.site.urls),
#     ...
# )