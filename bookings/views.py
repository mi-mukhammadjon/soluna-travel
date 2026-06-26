# bookings/views.py
from django.views.generic import ListView, DetailView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Booking
from .forms import BookingForm
from tours.models import Tour


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'   # ← MOSLASHTIRILDI
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).select_related('tour').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookings_count'] = self.get_queryset().count()
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'  # ← MOSLASHTIRILDI
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('tour')


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_create.html'  # ← MOSLASHTIRILDI

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, slug=kwargs['tour_slug'], is_active=True)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Tur sahifasidagi "Book Now" formasidan kelgan sana va mehmonlar
        sonini booking formasiga avtomatik to'ldiradi."""
        initial = super().get_initial()
        params = self.request.GET

        # Sana — tur sahifasida name="date" sifatida yuboriladi (YYYY-MM-DD)
        date = (params.get('date') or params.get('travel_date') or '').strip()
        if date:
            parsed = parse_date(date)
            if parsed and parsed >= timezone.now().date():
                # ISO string — <input type="date"> faqat YYYY-MM-DD qabul qiladi,
                # date obyekti template'da lokalizatsiya bo'lib ketadi.
                initial['travel_date'] = parsed.isoformat()

        try:
            adults = int(params.get('adults', ''))
            if adults >= 1:
                initial['num_adults'] = min(adults, 20)
        except (ValueError, TypeError):
            pass

        try:
            children = int(params.get('children', ''))
            if children >= 0:
                initial['num_children'] = min(children, 10)
        except (ValueError, TypeError):
            pass

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tour'] = self.tour
        try:
            num_adults = max(1, int(self.request.GET.get('adults', 1)))
        except (ValueError, TypeError):
            num_adults = 1
        context['estimated_price'] = self.tour.discounted_price * num_adults
        return context

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.tour = self.tour
        booking.price_per_person = self.tour.discounted_price
        booking.total_price = (
            self.tour.discounted_price * booking.num_adults
            + self.tour.child_price * booking.num_children
        )
        booking.status = 'pending'
        booking.save()

        try:
            from .tasks import send_booking_confirmation_email
            send_booking_confirmation_email.delay(booking.pk)
        except Exception:
            pass  # Celery ishlamasa ham bron yaratilsin

        messages.success(
            self.request,
            f"Bron muvaffaqiyatli yaratildi! Raqam: {booking.booking_number}"
        )
        return redirect(reverse('bookings:booking-detail', kwargs={'pk': booking.pk}))

    def form_invalid(self, form):
        # XATOLARNI BOSHQA SAHIFAGA YUBORISH O'RNIGA SHU SAHIFADA KO'RSATISH
        messages.error(
            self.request,
            "Iltimos, formada xato bo'lgan maydonlarni to'g'rilang."
        )
        return super().form_invalid(form)


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

        try:
            from .tasks import send_booking_cancellation_email
            send_booking_cancellation_email.delay(booking.pk)
        except Exception:
            pass

        messages.success(request, "Bron bekor qilindi.")
        return redirect(reverse('bookings:booking-list'))