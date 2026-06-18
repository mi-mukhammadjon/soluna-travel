from django.views.generic import CreateView, UpdateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User
from .forms import RegisterForm, ProfileUpdateForm


# class RegisterView(CreateView):
#     model = User
#     form_class = RegisterForm
#     template_name = 'accounts/register.html'
#     success_url = reverse_lazy('home')

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('home')
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)

#         # Email tasdiqlash va xush kelibsiz xabarlari
#         from .tasks import send_verification_email, send_welcome_email
#         send_verification_email.delay(user.pk)
#         send_welcome_email.delay(user.pk)

#         messages.success(self.request, f"Xush kelibsiz, {user.get_full_name()}! Emailingizni tasdiqlang.")
#         return redirect(self.success_url)


# class CustomLoginView(LoginView):
#     template_name = 'accounts/login.html'

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('home')
#         return super().dispatch(request, *args, **kwargs)

#     def get_success_url(self):
#         next_url = self.request.GET.get('next')
#         return next_url or reverse_lazy('home')


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings'] = self.request.user.bookings.select_related('tour').order_by('-created_at')[:5]
        context['reviews'] = self.request.user.reviews.select_related('tour').order_by('-created_at')[:5]
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


class EmailVerifyView(View):
    def get(self, request, token):
        user = get_object_or_404(User, email_verification_token=token)
        if not user.is_verified:
            user.is_verified = True
            user.save()
            messages.success(request, "Email muvaffaqiyatli tasdiqlandi!")
        else:
            messages.info(request, "Email allaqachon tasdiqlangan.")
        return redirect('home')


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        messages.success(self.request, "Parol muvaffaqiyatli o'zgartirildi.")
        return super().form_valid(form)
    
