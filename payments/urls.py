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

    # Webhooks — gateway tomonidan chaqiriladi
    path('webhook/click/', views.ClickWebhookView.as_view(), name='webhook-click'),
    path('webhook/payme/', views.PaymeWebhookView.as_view(), name='webhook-payme'),
    path('mock/<uuid:payment_id>/', views.MockPaymentView.as_view(), name='mock-pay')
]