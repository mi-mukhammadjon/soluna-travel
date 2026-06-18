from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from tours.models import Tour
from .models import Review
from .forms import ReviewForm


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.tour = get_object_or_404(Tour, slug=kwargs['tour_slug'])
        # Faqat bir marta izoh qoldirish mumkin
        if Review.objects.filter(user=request.user, tour=self.tour).exists():
            messages.warning(request, "Siz bu tur uchun allaqachon izoh qoldirganusiz.")
            return redirect(reverse('tours:tour-detail', kwargs={'slug': self.tour.slug}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tour'] = self.tour
        return context

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        review.tour = self.tour
        review.save()
        messages.success(self.request, "Izohingiz qabul qilindi va tasdiqlanish kutilmoqda.")
        return redirect(reverse('tours:tour-detail', kwargs={'slug': self.tour.slug}))


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.is_approved = False  # Tahrirlanganda qayta tasdiqlash kerak
        review.save()
        messages.success(self.request, "Izoh yangilandi.")
        return redirect(reverse('tours:tour-detail', kwargs={'slug': review.tour.slug}))


class ReviewDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk, user=request.user)
        tour_slug = review.tour.slug
        review.delete()
        messages.success(request, "Izoh o'chirildi.")
        return redirect(reverse('tours:tour-detail', kwargs={'slug': tour_slug}))