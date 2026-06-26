# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # User-facing
    path('<int:booking_id>/',          views.PaymentSelectView.as_view(),   name='select'),
    path('<int:booking_id>/initiate/', views.PaymentInitiateView.as_view(), name='initiate'),
    path('<int:booking_id>/success/',  views.PaymentSuccessView.as_view(),  name='success'),
    path('<int:booking_id>/failed/',   views.PaymentFailedView.as_view(),   name='failed'),

    # Return from gateway
    path('return/<uuid:payment_id>/',  views.PaymentReturnView.as_view(),   name='return'),

    # AJAX status check
    path('status/<uuid:payment_id>/',  views.PaymentStatusAPIView.as_view(), name='status'),

    # Webhooks — config.urls'da i18n_patterns'dan TASHQARIDA ulandi
    # (payments/webhook_urls.py), chunki gateway POST'lari til prefiksli
    # redirect'ga ergashmaydi.

    path('mock/<uuid:payment_id>/', views.MockPaymentView.as_view(), name='mock-pay')
]