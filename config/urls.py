# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse
from config.admin_dashboard import dashboard_stats
from config.sitemaps import SITEMAPS
from accounts.views import CustomSignupView


def _yandex_verify(request, code):
    """Yandex Webmaster HTML-fayl usuli — /yandex_<code>.html 200 OK qaytaradi."""
    return HttpResponse(
        f'<html><head><meta name="yandex-verification" content="{code}" /></head>'
        f'<body>Verification: {code}</body></html>',
        content_type='text/html',
    )


def _google_verify(request, code):
    """Google Search Console HTML-fayl usuli — /google<code>.html."""
    return HttpResponse(f'google-site-verification: google{code}.html',
                        content_type='text/html')


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    # SEO — til prefiksisiz (i18n_patterns'dan TASHQARIDA)
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),

    # Qidiruv tizimlari HTML-fayl tasdiqlash (Yandex/Google)
    path('yandex_<str:code>.html', _yandex_verify),
    path('google<str:code>.html', _google_verify),

    # Gateway webhooks — til prefiksisiz (i18n_patterns'dan TASHQARIDA bo'lishi shart,
    # aks holda Click/Payme POST'lari /uz/... ga redirect bo'lib uziladi).
    path('', include('payments.webhook_urls')),

    # ── Auth — til prefiksisiz (i18n_patterns'dan TASHQARIDA) ──────────────
    # MUHIM: allauth social callback URL'i (/accounts/google/login/callback/)
    # til prefiksisiz, o'zgarmas bo'lishi kerak — aks holda Google OAuth
    # redirect_uri_mismatch beradi. Sahifalar baribir aktiv tilda ko'rsatiladi.
    path('accounts/signup/', CustomSignupView.as_view(), name='account_signup'),  # custom, allauth'dan oldin
    path('accounts/', include('accounts.urls')),                                   # profil/parol, allauth'dan oldin
    path('accounts/', include('allauth.urls')),                                    # login/logout/social
]

urlpatterns += i18n_patterns(
    path("solunasuperuse/dashboard-stats/", dashboard_stats, name="admin-dashboard-stats"),
    path('solunasuperuse/', admin.site.urls),

    # ── Applar ────────────────────────────────────────────
    # (Auth i18n_patterns'dan TASHQARIGA ko'chirildi — yuqoriga qarang)
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