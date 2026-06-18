# config/admin_dashboard.py
"""
SoLuna Admin Dashboard — statistika endpointi.

ESKI YONDASHUV MUAMMOSI:
Dashboard JS 4 ta admin changelist sahifasini to'liq yuklab,
regex bilan HTML dan raqam qidirardi:
  - 4 ta og'ir HTTP so'rov (har biri to'liq render + queryset)
  - Til o'zgarsa regex buziladi ("result" vs "объект" vs "natija")
  - pagination 100 dan oshsa noto'g'ri sanaydi

YANGI YONDASHUV: bitta yengil JSON endpoint, ORM .count() bilan.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_GET

from accounts.models import User
from bookings.models import Booking
from messages_app.models import ContactMessage
from tours.models import Tour


@require_GET
@staff_member_required
def dashboard_stats(request):
    """KPI raqamlari + oxirgi yozuvlar — bitta so'rovda."""
    recent_bookings = (
        Booking.objects
        .select_related("user", "tour")           # N+1 oldini olish
        .order_by("-created_at")[:5]
    )
    recent_messages = (
        ContactMessage.objects
        .filter(status="new")
        .order_by("-created_at")[:5]
    )

    return JsonResponse({
        "kpi": {
            "bookings": Booking.objects.count(),
            "new_messages": ContactMessage.objects.filter(status="new").count(),
            "active_tours": Tour.objects.filter(is_active=True).count(),
            "users": User.objects.filter(is_staff=False).count(),
            "pending_bookings": Booking.objects.filter(status="pending").count(),
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
                "url": reverse(
                    "admin:messages_app_contactmessage_change", args=[m.pk]
                ),
            }
            for m in recent_messages
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