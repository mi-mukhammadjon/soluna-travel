# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from config.admin_dashboard import dashboard_stats
from accounts.views import CustomSignupView


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # Gateway webhooks — til prefiksisiz (i18n_patterns'dan TASHQARIDA bo'lishi shart,
    # aks holda Click/Payme POST'lari /uz/... ga redirect bo'lib uziladi).
    path('', include('payments.webhook_urls')),
]

urlpatterns += i18n_patterns(
    path("solunasuperuse/dashboard-stats/", dashboard_stats, name="admin-dashboard-stats"),
    path('solunasuperuse/', admin.site.urls),

    # ── Auth ──────────────────────────────────────────────
    # Custom signup — allauth'dan oldin, shunda custom view ishlatiladi
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),

    # Custom accounts app — profil + parol o'zgartirish.
    # MUHIM: allauth'dan OLDIN, aks holda allauth '/accounts/password/change/' ni o'g'irlaydi.
    path('accounts/', include('accounts.urls')),

    # Allauth — login, logout, password reset, social login
    path('accounts/', include('allauth.urls')),

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

handler404 = 'tours.views.custom_404_view'
handler500 = 'tours.views.custom_500_view'

# Buni oxiriga qo'shasiz
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)