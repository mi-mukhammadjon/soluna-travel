from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<int:booking_id>/', views.PaymentSelectView.as_view(), name='select'),
    path('click/return/', views.ClickReturnView.as_view(), name='click-return'),
    path('click/webhook/', views.ClickWebhookView.as_view(), name='click-webhook'),
    path('payme/webhook/', views.PaymeWebhookView.as_view(), name='payme-webhook'),
]