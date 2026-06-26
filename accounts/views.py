from django.shortcuts import redirect
from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from allauth.account.views import SignupView as AllauthSignupView
from .models import User
from .forms import ProfileUpdateForm


class CustomSignupView(AllauthSignupView):
    """Signup dan keyin login sahifasiga redirect"""

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.contrib.auth import logout
        logout(self.request)
        messages.success(self.request, "Hisobingiz yaratildi! Endi tizimga kiring.")
        return redirect(reverse('account_login'))


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        u = self.request.user
        bookings = u.bookings.select_related('tour').order_by('-created_at')
        reviews = u.reviews.select_related('tour').order_by('-created_at')
        wishlist = u.wishlist.select_related('tour').order_by('-created_at')
        context['bookings'] = bookings
        context['reviews'] = reviews
        context['wishlist_items'] = wishlist
        context['stat_bookings'] = bookings.count()
        context['stat_completed'] = bookings.filter(status='completed').count()
        context['stat_wishlist'] = wishlist.count()
        context['stat_reviews'] = reviews.count()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profil yangilandi.")
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        messages.success(self.request, "Parol muvaffaqiyatli o'zgartirildi.")
        return super().form_valid(form)

