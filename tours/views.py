from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Avg, Count, F, Case, When, Value, BooleanField
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Tour, TourCategory, CompanyStatistic, CompanyAdvantage, Wishlist
from regions.models import Region
from django.views.decorators.cache import cache_page

# Nav "tour type" tugmalarini haqiqiy filtrlarga bog'laydi
# (cultural → kategoriya, adventure → qiyinlik, premium → tanlangan)
def filter_by_tour_type(qs, tour_type):
    tour_type = (tour_type or '').strip()
    if tour_type == 'cultural':
        return qs.filter(category__slug='cultural-tour')
    if tour_type == 'adventure':
        return qs.filter(difficulty__in=['medium', 'hard'])
    if tour_type == 'premium':
        return qs.filter(is_featured=True)
    return qs


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        from django.core.cache import cache
        context = super().get_context_data(**kwargs)

        # Statik ma'lumotlar — 5 daqiqa keshda
        regions = cache.get('home_regions')
        if regions is None:
            regions = list(Region.objects.annotate(tour_count=Count('tours')).order_by('-tour_count'))
            cache.set('home_regions', regions, 300)

        categories = cache.get('home_categories')
        if categories is None:
            categories = list(TourCategory.objects.annotate(tour_count=Count('tour'))[:8])
            cache.set('home_categories', categories, 300)

        featured_tours = cache.get('home_featured_tours')
        if featured_tours is None:
            featured_tours = list(
                Tour.objects.filter(is_active=True, is_featured=True)
                .annotate(
                    avg_rating=Avg('reviews__rating'),
                    review_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
                    booking_count=Count('bookings', distinct=True),
                )
                .select_related('category')
                .prefetch_related('regions')[:6]
            )
            cache.set('home_featured_tours', featured_tours, 300)

        context['regions'] = regions
        context['categories'] = categories
        context['featured_tours'] = featured_tours
        context['company_stats'] = cache.get_or_set(
            'home_company_stats', lambda: list(CompanyStatistic.objects.all()[:4]), 600
        )
        context['company_advantages'] = cache.get_or_set(
            'home_company_advantages', lambda: list(CompanyAdvantage.objects.all()[:4]), 600
        )
        context['popular_destinations'] = regions[:6]
        return context

# tours/views.py — Search filter integration
class TourListView(ListView):
    model = Tour
    template_name = 'tours/list.html'
    context_object_name = 'tours'
    paginate_by = 12

    def get_queryset(self):
        qs = Tour.objects.filter(is_active=True).prefetch_related('regions')
        
        sixty_days_ago = timezone.now() - timedelta(days=60)
        qs = qs.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
            booking_count=Count('bookings', distinct=True),
            is_new_tour=Case(
                When(created_at__gte=sixty_days_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        # ── q (qidiruv) ──
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(title_uz__icontains=q) |
                Q(title_ru__icontains=q) |
                Q(title_en__icontains=q) |
                Q(short_description__icontains=q) |
                Q(short_description_uz__icontains=q) |
                Q(short_description_ru__icontains=q) |
                Q(regions__name__icontains=q) |
                Q(regions__name_uz__icontains=q) |
                Q(regions__name_ru__icontains=q)
            ).distinct()

        # ── category filter ──
        categories = self.request.GET.getlist('category')
        if categories:
            qs = qs.filter(category__slug__in=categories)

        # ── tour type (nav: cultural / adventure / premium) ──
        qs = filter_by_tour_type(qs, self.request.GET.get('type'))

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

        # ── featured ──
        if self.request.GET.get('featured') == '1':
            qs = qs.filter(is_featured=True)

        # ── price range (min_price / max_price) ──
        try:
            min_price = self.request.GET.get('min_price')
            if min_price:
                qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
            
        try:
            max_price = self.request.GET.get('max_price')
            if max_price:
                qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass

        # ── rating filter ──
        rating = self.request.GET.get('rating', '').strip()
        if rating:
            try:
                min_rating = float(rating)
                qs = qs.filter(Q(avg_rating__gte=min_rating) | Q(avg_rating__isnull=True))
            except ValueError:
                pass

        # ── city query ──
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
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'rating':
            qs = qs.order_by('-avg_rating')
        else:  # popular
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
        
        # Kategoriyalar (tour_count bilan)
        context['categories'] = TourCategory.objects.annotate(
            tour_count=Count('tour')
        )
        
        context['popular_destinations'] = Region.objects.annotate(
            tour_count=Count('tours')
        ).order_by('-tour_count')[:6]

        if self.request.user.is_authenticated:
            context['wishlisted_ids'] = set(
                Wishlist.objects.filter(user=self.request.user).values_list('tour_id', flat=True)
            )
        else:
            context['wishlisted_ids'] = set()

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

        # O'xshash turlar — tavsiya etilgan / tanlangan / chegirmali turlar oldinda
        context['similar_tours'] = Tour.objects.filter(
            is_active=True,
            regions__in=tour.regions.all()
        ).exclude(pk=tour.pk).annotate(
            avg_rating=Avg('reviews__rating')
        ).distinct().order_by('-is_recommended', '-is_featured', '-discount_percent', '-created_at')[:4]

        context['is_wishlisted'] = (
            self.request.user.is_authenticated and
            Wishlist.objects.filter(user=self.request.user, tour=tour).exists()
        )

        # Foydalanuvchining tasdiqlangan bo'lmagan (pending) sharhi
        context['pending_review'] = (
            tour.reviews.filter(user=self.request.user, is_approved=False).first()
            if self.request.user.is_authenticated else None
        )

        return context


def tour_filter_api(request):
    """AJAX filter uchun API — turlarni JSON formatda qaytaradi"""
    from django.template.loader import render_to_string
    
    qs = Tour.objects.filter(is_active=True).prefetch_related('regions')
    sixty_days_ago = timezone.now() - timedelta(days=60)
    qs = qs.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
        booking_count=Count('bookings', distinct=True),
        is_new_tour=Case(
            When(created_at__gte=sixty_days_ago, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

    # ── q (qidiruv) ──
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(title_uz__icontains=q) |
            Q(title_ru__icontains=q) |
            Q(title_en__icontains=q) |
            Q(short_description__icontains=q) |
            Q(short_description_uz__icontains=q) |
            Q(short_description_ru__icontains=q) |
            Q(regions__name__icontains=q) |
            Q(regions__name_uz__icontains=q) |
            Q(regions__name_ru__icontains=q)
        ).distinct()

    # ── category ──
    categories = request.GET.getlist('category')
    if categories:
        qs = qs.filter(category__slug__in=categories)

    # ── tour type (nav: cultural / adventure / premium) ──
    qs = filter_by_tour_type(qs, request.GET.get('type'))

    # ── duration ──
    duration = request.GET.get('duration', '').strip()
    if duration == '1-3':
        qs = qs.filter(duration_days__gte=1, duration_days__lte=3)
    elif duration == '4-7':
        qs = qs.filter(duration_days__gte=4, duration_days__lte=7)
    elif duration == '8-14':
        qs = qs.filter(duration_days__gte=8, duration_days__lte=14)
    elif duration == '15+':
        qs = qs.filter(duration_days__gte=15)

    # ── featured ──
    if request.GET.get('featured') == '1':
        qs = qs.filter(is_featured=True)

    # ── price range ──
    try:
        min_price = request.GET.get('min_price')
        if min_price:
            qs = qs.filter(price__gte=float(min_price))
    except ValueError:
        pass
    try:
        max_price = request.GET.get('max_price')
        if max_price:
            qs = qs.filter(price__lte=float(max_price))
    except ValueError:
        pass

    # ── rating ──
    rating = request.GET.get('rating', '').strip()
    if rating:
        try:
            min_rating = float(rating)
            # NULL avg_rating ga ega turlarni ham qo'shamiz (review yo'q hali)
            qs = qs.filter(Q(avg_rating__gte=min_rating) | Q(avg_rating__isnull=True))
        except ValueError:
            pass

    # ── city ──
    city = request.GET.get('city', '').strip()
    if city:
        qs = qs.filter(
            Q(regions__slug__iexact=city) |
            Q(regions__name__icontains=city)
        ).distinct()

    # ── sort ──
    sort = request.GET.get('sort', 'popular')
    if sort == 'newest':
        qs = qs.order_by('-created_at')
    elif sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'rating':
        qs = qs.order_by('-avg_rating')
    else:
        qs = qs.order_by('-is_featured', '-avg_rating', '-created_at')

    # ── pagination ──
    page = int(request.GET.get('page', 1))
    per_page = 12
    total = qs.count()
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    tours = qs[start:start + per_page]

    # ── HTML render ──
    wishlisted_ids = set()
    if request.user.is_authenticated:
        wishlisted_ids = set(Wishlist.objects.filter(user=request.user).values_list('tour_id', flat=True))

    tours_html = render_to_string('tours/_tour_cards.html', {
        'tours': tours,
        'wishlisted_ids': wishlisted_ids,
    }, request=request)

    pagination_html = render_to_string('tours/_pagination.html', {
        'page': page,
        'total_pages': total_pages,
        'page_range': range(1, total_pages + 1),
    }, request=request)

    return JsonResponse({
        'tours_html': tours_html,
        'pagination_html': pagination_html,
        'total': total,
        'page': page,
        'total_pages': total_pages,
    })


@require_POST
def wishlist_toggle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required'}, status=401)
    tour = get_object_or_404(Tour, pk=pk, is_active=True)
    obj, created = Wishlist.objects.get_or_create(user=request.user, tour=tour)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})