from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, ReplyForm


# ── Anti-bot: IP bo'yicha rate-limit (1 soatda maksimal yuborishlar) ──
CONTACT_MAX_PER_HOUR = 5


def _client_ip(request):
    """Nginx orqasida bo'lsa ham to'g'ri IP (X-Forwarded-For dagi birinchi)."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _verify_turnstile(request):
    """Cloudflare Turnstile — faqat kalitlar sozlangan bo'lsa tekshiradi.
    Kalit yo'q bo'lsa True (o'tkazadi) — honeypot/time-trap/rate-limit himoya qiladi."""
    secret = getattr(settings, 'TURNSTILE_SECRET_KEY', '')
    if not secret:
        return True
    token = request.POST.get('cf-turnstile-response', '')
    if not token:
        return False
    try:
        import requests
        r = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': secret, 'response': token, 'remoteip': _client_ip(request)},
            timeout=5,
        )
        return bool(r.json().get('success'))
    except Exception:
        # Turnstile serveriga ulanib bo'lmasa, boshqa qatlamlar himoya qiladi
        return True


class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'messages_app/contact.html'
    success_url = reverse_lazy('messages_app:contact-success')

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['name'] = self.request.user.get_full_name()
            initial['email'] = self.request.user.email
            initial['phone'] = self.request.user.phone
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['turnstile_site_key'] = getattr(settings, 'TURNSTILE_SITE_KEY', '')
        return ctx

    def form_valid(self, form):
        # ── Rate-limit: IP bo'yicha soatiga cheklov ──
        ip = _client_ip(self.request)
        rl_key = 'contact_rl:%s' % ip
        if cache.get(rl_key, 0) >= CONTACT_MAX_PER_HOUR:
            form.add_error(None, _('Too many messages. Please try again later.'))
            return self.form_invalid(form)

        # ── Cloudflare Turnstile (agar sozlangan bo'lsa) ──
        if not _verify_turnstile(self.request):
            form.add_error(None, _('Please confirm you are not a robot.'))
            return self.form_invalid(form)

        msg = form.save(commit=False)
        if self.request.user.is_authenticated:
            msg.user = self.request.user
        msg.save()

        # rate-limit hisoblagichini oshiramiz
        try:
            cache.set(rl_key, cache.get(rl_key, 0) + 1, 3600)
        except Exception:
            pass

        from .tasks import notify_admin_new_message
        notify_admin_new_message.delay(msg.pk)

        return redirect(self.success_url)


class ContactSuccessView(View):
    def get(self, request):
        return render(request, 'messages_app/contact_success.html')


class MessageReplyView(UserPassesTestMixin, View):
    """Admin tomonidan xabarga javob berish"""

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        form = ReplyForm(instance=msg)
        return render(request, 'messages_app/reply.html', {'msg': msg, 'form': form})

    def post(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        form = ReplyForm(request.POST, instance=msg)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.status = 'replied'
            reply.replied_at = timezone.now()
            reply.replied_by = request.user
            reply.save()

            from .tasks import send_reply_email
            send_reply_email.delay(msg.pk)

            messages.success(request, "Javob yuborildi.")
            return redirect(reverse('admin:messages_app_contactmessage_change', args=[pk]))

        return render(request, 'messages_app/reply.html', {'msg': msg, 'form': form})


class NewsletterSubscribeView(View):
    def post(self, request):
        email = request.POST.get('email', '').strip()
        if not email:
            return JsonResponse({'ok': False, 'error': 'Email kiritilmadi.'}, status=400)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.unsubscribed_at = None
            subscriber.save()
            created = True

        if created:
            return JsonResponse({'ok': True, 'message': 'Obuna muvaffaqiyatli amalga oshirildi!'})
        return JsonResponse({'ok': True, 'message': 'Siz allaqachon obuna bo\'lgansiz.'})
