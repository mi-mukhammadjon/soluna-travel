# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ╔════════════════════════════════════════════════════════════╗
    # ║ Login, signup, logout, password-reset — ALLAUTH boshqaradi║
    # ║ (allauth.urls orqali). Shu yerdan OLIB TASHLANDI.        ║
    # ║                                                            ║
    # ║ Allauth URL nomlari:                                       ║
    # ║   account_login    → /accounts/login/                      ║
    # ║   account_signup   → /accounts/signup/                     ║
    # ║   account_logout   → /accounts/logout/                     ║
    # ║   account_reset_password → /accounts/password/reset/       ║
    # ║                                                            ║
    # ║ Templatelar: templates/account/ (s YO'Q) papkasida         ║
    # ╚════════════════════════════════════════════════════════════╝

    # Profil sahifalari — faqat authenticated foydalanuvchilar uchun
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile-edit'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password-change'),
]