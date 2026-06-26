from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse
from .models import ContactMessage, NewsletterSubscriber
from .forms import ContactForm, ReplyForm


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

    def form_valid(self, form):
        msg = form.save(commit=False)
        if self.request.user.is_authenticated:
            msg.user = self.request.user
        msg.save()

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
