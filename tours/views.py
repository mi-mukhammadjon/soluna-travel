from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg, Count
from .models import Tour, TourCategory, CompanyStatistic, CompanyAdvantage
from regions.models import Region


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
        return context


class TourListView(ListView):
    model = Tour
    template_name = 'tours/list.html'
    context_object_name = 'tours'
    paginate_by = 12

    def get_queryset(self):
        # Boshlang'ich QuerySet va SQL joinlarni kamaytirish uchun select_related/prefetch_related
        # Modelda setter borligi sababli avg_rating annotatsiyasi xavfsiz ishlaydi
        qs = Tour.objects.filter(is_active=True).select_related('category').prefetch_related('regions')

        # 1. Qidiruv (Search)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        # 2. Kategoriya filtri
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category__slug=category)

        # 3. Region filtri
        region = self.request.GET.get('region')
        if region:
            qs = qs.filter(regions__slug=region)

        # 4. Narx filtri (Min / Max)
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        # 5. Davomiylik filtri (Duration)
        duration = self.request.GET.get('duration')
        if duration == '1-3':
            qs = qs.filter(duration_days__lte=3)
        elif duration == '4-7':
            qs = qs.filter(duration_days__gte=4, duration_days__lte=7)
        elif duration == '8+':
            qs = qs.filter(duration_days__gte=8)

        # Filtrlar tugagandan keyin yulduzchalarni hisoblaymiz (SQL hisob-kitob to'g'ri bo'lishi uchun)
        qs = qs.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews', distinct=True)
        )

        # 6. Saralash (Sorting) - endi '-avg_rating' muammosiz saralaydi
        sort = self.request.GET.get('sort', '-created_at')
        allowed_sorts = ['price', '-price', 'duration_days', '-duration_days', '-created_at', '-avg_rating']
        if sort in allowed_sorts:
            qs = qs.order_by(sort)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = TourCategory.objects.annotate(tour_count=Count('tour'))
        context['regions'] = Region.objects.filter(is_active=True)
        
        # OPTIMIZATSIYA: self.get_queryset().count() o'rniga allaqachon chaqirilgan object_list dan foydalanamiz
        # Bu bazaga ortiqcha va og'ir takroriy so'rov yuborilishining oldini oladi
        context['total_count'] = self.object_list.count()
        
        # Filtr qiymatlarini templatega qaytaramiz (Formlarda saqlanib qolishi uchun)
        context['filters'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'region': self.request.GET.get('region', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'duration': self.request.GET.get('duration', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
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