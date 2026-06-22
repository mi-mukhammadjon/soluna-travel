from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from regions.models import Attraction
from .models import NearbyPlace
from .dgis import search_nearby


@method_decorator(cache_page(60 * 30), name='dispatch')  # 30 daqiqa cache
class NearbyPlacesAPIView(View):
    """
    Yaqin atrofdagi joylarni qaytaruvchi API.
    GET /places/nearby/?lat=41.2&lon=69.2&category=cafe&radius=500
    """

    def get(self, request):
        try:
            lat = float(request.GET.get('lat', 0))
            lon = float(request.GET.get('lon', 0))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'lat va lon kerak'}, status=400)

        category = request.GET.get('category', 'cafe')
        try:
            radius = min(int(request.GET.get('radius', 1000)), 5000)
        except (ValueError, TypeError):
            radius = 1000

        if not lat or not lon:
            return JsonResponse({'error': 'lat va lon noto\'g\'ri'}, status=400)

        # Avval DB dan qidirish
        db_places = NearbyPlace.objects.filter(
            is_active=True,
            category=category,
            latitude__range=(lat - 0.01, lat + 0.01),
            longitude__range=(lon - 0.01, lon + 0.01),
        ).values('id', 'name', 'category', 'address', 'latitude', 'longitude',
                 'phone', 'website', 'rating', 'source')

        if db_places.exists():
            return JsonResponse({'results': list(db_places), 'source': 'db'})

        # DB da yo'q — 2GIS dan qidirish
        results = search_nearby(lat, lon, category=category, radius=radius)

        # DB ga saqlash (keyingi so'rovlar tezroq bo'lsin)
        for place in results:
            NearbyPlace.objects.get_or_create(
                external_id=place['external_id'],
                defaults={**place, 'source': '2gis'}
            )

        return JsonResponse({'results': results, 'source': '2gis'})


class AttractionNearbyView(View):
    """
    Attraksiya atrofidagi joylar.
    GET /places/attraction/<id>/nearby/?category=cafe
    """

    def get(self, request, attraction_id):
        attraction = get_object_or_404(Attraction, pk=attraction_id)

        if not attraction.latitude or not attraction.longitude:
            return JsonResponse({'error': 'Bu attraksiyada koordinatalar yo\'q'}, status=400)

        category = request.GET.get('category', 'cafe')
        try:
            radius = int(request.GET.get('radius', 1000))
        except (ValueError, TypeError):
            radius = 1000

        results = search_nearby(
            float(attraction.latitude),
            float(attraction.longitude),
            category=category,
            radius=radius
        )

        return JsonResponse({
            'attraction': attraction.name,
            'results': results
        })