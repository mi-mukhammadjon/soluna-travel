from django.urls import path
from . import views

app_name = 'messages_app'

urlpatterns = [
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact-success'),
    path('reply/<int:pk>/', views.MessageReplyView.as_view(), name='reply'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
]