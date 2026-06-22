from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg, Count
from .models import Tour, TourCategory, CompanyStatistic, CompanyAdvantage
from regions.models import Region
from django.views.decorators.cache import cache_page

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Barcha turlarni olamiz
        tours = Tour.objects.filter(is_active=True)

        # 2. URL'dan GET parametrlarni o'qiymiz
        category = self.request.GET.get('category')
        duration = self.request.GET.get('duration')
        price = self.request.GET.get('price')

        # 3. Kategoriya bo'yicha filter
        if category:
            # Agar modelingizda kategoriya maydoni boshqacha nomlangan bo'lsa, shunga moslang (masalan category__name)
            tours = tours.filter(category__slug=category) 

        # 4. Davomiylik bo'yicha filter (duration maydoni qanday turda ekanligiga qarab o'zgartirasiz)
        if duration:
            if duration == '1-3':
                tours = tours.filter(duration_days__lte=3)
            elif duration == '4-7':
                tours = tours.filter(duration_days__gte=4, duration_days__lte=7)
            elif duration == '8+':
                tours = tours.filter(duration_days__gte=8)

        # 5. Narx bo'yicha filter
        if price:
            if price == '0-500':
                tours = tours.filter(price__lte=500)
            elif price == '500-1000':
                tours = tours.filter(price__gt=500, price__lte=1000)
            elif price == '1000+':
                tours = tours.filter(price__gt=1000)
        
        # 1. Kategoriyalarni va ularning ichidagi turlar sonini hisoblab 8 tasini olamiz
        # DIQQAT: 'tour' so'zi Tour modelingizning related_name'iga qarab 'tours' yoki 'tour_set' bo'lishi mumkin.
        context['categories'] = TourCategory.objects.annotate(
            tour_count=Count('tour') 
        )[:8]
        
        context['featured_tours'] = Tour.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category').prefetch_related('regions')[:6]
        
        context['regions'] = Region.objects.annotate(tour_count=Count('tours'))
        context['company_stats'] = CompanyStatistic.objects.all()[:4]
        context['company_advantages'] = CompanyAdvantage.objects.all()[:4]
        context['popular_destinations'] = Region.objects.annotate(
            tour_count=Count('tours')
        ).order_by('-tour_count')[:6]
        return context

# tours/views.py — Search filter integration
class TourListView(ListView):
    model = Tour
    template_name = 'tours/list.html'
    context_object_name = 'tours'
    paginate_by = 12

    def get_queryset(self):
        qs = Tour.objects.filter(is_active=True).prefetch_related('regions')
        
        # 1-TUZATISH: Sharhlarning o'rtacha qiymatini (avg_rating) hisoblaymiz
        qs = qs.annotate(avg_rating=Avg('reviews__rating'))

        # ── q (location/destination/title) ──
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(title_uz__icontains=q) |
                Q(title_ru__icontains=q) |
                Q(title_en__icontains=q) |
                Q(short_description__icontains=q) |
                Q(regions__name__icontains=q) |
                Q(regions__name_uz__icontains=q) |
                Q(regions__name_ru__icontains=q)
            ).distinct()

        # ── travel_date (faqat shu sanada mavjud turlar) ──
        travel_date = self.request.GET.get('travel_date', '').strip()
        if travel_date:
            pass

        # ── duration (1-3 / 4-7 / 8-14 / 15+) ──
        duration = self.request.GET.get('duration', '').strip()
        if duration == '1-3':
            qs = qs.filter(duration_days__gte=1, duration_days__lte=3)
        elif duration == '4-7':
            qs = qs.filter(duration_days__gte=4, duration_days__lte=7)
        elif duration == '8-14':
            qs = qs.filter(duration_days__gte=8, duration_days__lte=14)
        elif duration == '15+':
            qs = qs.filter(duration_days__gte=15)

        # ── tour_type (Cultural / Adventure / Premium) ──
        tour_type = self.request.GET.get('type', '').strip()
        if tour_type:
            qs = qs.filter(tour_type__iexact=tour_type)

        # ── activity_type (alohida URL: ?featured=1&activity_type=...) ──
        activity = self.request.GET.get('activity_type', '').strip()
        if activity:
            qs = qs.filter(tour_type__iexact=activity)

        # ── featured (Activities tab) ──
        if self.request.GET.get('featured') == '1':
            qs = qs.filter(is_featured=True)

        # ── price range ──
        try:
            price_min = self.request.GET.get('price_min')
            if price_min:
                qs = qs.filter(price__gte=float(price_min))
        except ValueError:
            pass
            
        try:
            price_max = self.request.GET.get('price_max')
            if price_max:
                qs = qs.filter(price__lte=float(price_max))
        except ValueError:
            pass

        # ── city query (Destinations dropdown'dan ?city=samarkand) ──
        city = self.request.GET.get('city', '').strip()
        if city:
            qs = qs.filter(
                Q(regions__slug__iexact=city) |
                Q(regions__name__icontains=city)
            ).distinct()

        # ── Sorting ──
        sort = self.request.GET.get('sort', 'popular')
        if sort == 'newest':
            qs = qs.order_by('-created_at')
        elif sort == 'price_low':
            qs = qs.order_by('price')
        elif sort == 'price_high':
            qs = qs.order_by('-price')
        elif sort == 'rating':
            # 2-TUZATISH: 'rating' o'rniga biz hisoblagan 'avg_rating' ishlatiladi
            qs = qs.order_by('-avg_rating')
        else:  # popular
            # 3-TUZATISH: 'rating' o'rniga 'avg_rating'
            qs = qs.order_by('-is_featured', '-avg_rating', '-created_at')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['search'] = {
            'q': self.request.GET.get('q', ''),
            'travel_date': self.request.GET.get('travel_date', ''),
            'duration': self.request.GET.get('duration', ''),
            'adults': self.request.GET.get('adults', '2'),
            'children': self.request.GET.get('children', '0'),
            'sort': self.request.GET.get('sort', 'popular'),
            'tour_type': self.request.GET.get('type', ''),
            'city': self.request.GET.get('city', ''),
        }
        
        context['total_count'] = self.get_queryset().count()
        
        context['popular_destinations'] = Region.objects.annotate(
            tour_count=Count('tours')
        ).order_by('-tour_count')[:6]
        
        return context

class TourDetailView(DetailView):
    model = Tour
    template_name = 'tours/detail.html'
    context_object_name = 'tour'

    def get_queryset(self):
        return Tour.objects.filter(is_active=True) \
            .select_related('category') \
            .prefetch_related('regions', 'attractions', 'images', 'reviews__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour = self.object

        # Faqat tasdiqlangan (is_approved=True) sharhlarni ajratib olamiz
        reviews = tour.reviews.filter(is_approved=True).select_related('user')
        context['reviews'] = reviews
        context['avg_rating'] = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context['review_count'] = reviews.count()

        # Rating taqsimoti (5,4,3,2,1 yulduzchalar paneli uchun)
        review_count = context['review_count']
        rating_dist = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_dist[i] = {
                'count': count,
                'percent': round(count / review_count * 100) if review_count else 0
            }
        context['rating_dist'] = rating_dist

        # O'xshash turlar (Kategoriya va reyting annotatsiyasi bilan birga)
        context['similar_tours'] = Tour.objects.filter(
            is_active=True,
            regions__in=tour.regions.all()
        ).exclude(pk=tour.pk).annotate(
            avg_rating=Avg('reviews__rating')
        ).distinct()[:4]

        return context