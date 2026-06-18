from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .models import Booking
from .forms import BookingForm
from tours.models import Tour


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('tour').order_by('-created_at')


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('tour')


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, slug=kwargs['tour_slug'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tour'] = self.tour
        # Narx hisoblash preview uchun
        num_adults = int(self.request.GET.get('adults', 1))
        context['estimated_price'] = self.tour.price * num_adults
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.tour = self.tour
        booking.price_per_person = self.tour.price
        booking.total_price = self.tour.price * booking.num_adults
        booking.status = 'pending'
        booking.save()

        # Email yuborish (Celery orqali)
        from .tasks import send_booking_confirmation_email
        send_booking_confirmation_email.delay(booking.pk)

        messages.success(
            self.request,
            f"Bron muvaffaqiyatli yaratildi! Raqam: {booking.booking_number}"
        )
        return redirect(reverse('bookings:booking-detail', kwargs={'pk': booking.pk}))


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)

        if not booking.can_cancel:
            messages.error(request, "Bu bronni bekor qilib bo'lmaydi.")
            return redirect(reverse('bookings:booking-detail', kwargs={'pk': pk}))

        reason = request.POST.get('reason', '')
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save()

        from .tasks import send_booking_cancellation_email
        send_booking_cancellation_email.delay(booking.pk)

        messages.success(request, "Bron bekor qilindi.")
        return redirect(reverse('bookings:booking-list'))