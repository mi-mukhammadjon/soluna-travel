# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from config.admin_dashboard import dashboard_stats
from django.conf.urls import handler404, handler500 # Buni qo'shish kerak


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path("solunasuperuse/dashboard-stats/", dashboard_stats, name="admin-dashboard-stats"),
    path('solunasuperuse/', admin.site.urls),

    # ── Auth ──────────────────────────────────────────────
    # Allauth BIRINCHI — login, signup, logout, password reset,
    # social login (Google) hammasini boshqaradi.
    # URL nomlari: account_login, account_signup, account_logout, ...
    path('accounts/', include('allauth.urls')),

    # Custom accounts app — FAQAT profil sahifalari.
    # Login/signup/logout shu yerdan OLIB TASHLANGAN (allauth da bor).
    # URL nomlari: accounts:profile, accounts:profile-edit, accounts:password-change
    path('accounts/', include('accounts.urls')),

    # ── Boshqa applar ────────────────────────────────────
    path('regions/', include('regions.urls')),
    path('tours/', include('tours.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
    path('messages/', include('messages_app.urls')),
    path('reviews/', include('reviews.urls')),
    path('places/', include('places.urls')),
    path('', include('tours.urls_home')),

    prefix_default_language=True,
)

# Buni oxiriga qo'shasiz
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    handler404 = 'tours.views.custom_404_view'
    handler500 = 'tours.views.custom_500_view'