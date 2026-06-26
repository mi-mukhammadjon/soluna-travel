# payments/webhook_urls.py
# ─────────────────────────────────────────────────────────────
# Gateway webhook endpointlari — TIL PREFIKSISIZ barqaror URL.
#
# Click/Payme qat'iy (hardcoded) URL'ga server-to-server POST yuboradi
# va HTTP redirect (302)'ga ergashmaydi. Agar bu URL'lar i18n_patterns
# ichida bo'lsa, Django ularni /uz/... ga yo'naltiradi va webhook uziladi.
# Shuning uchun bular config.urls'da i18n_patterns'dan TASHQARIDA ulanadi.
#
# Gateway kabinetida ko'rsatiladigan URL:
#   https://<domen>/payments/webhook/click/
#   https://<domen>/payments/webhook/payme/
# ─────────────────────────────────────────────────────────────
from django.urls import path
from . import views

urlpatterns = [
    path('payments/webhook/click/', views.ClickWebhookView.as_view(), name='webhook-click'),
    path('payments/webhook/payme/', views.PaymeWebhookView.as_view(), name='webhook-payme'),
]
