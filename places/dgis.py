"""
2GIS API integratsiyasi.
Docs: https://docs.2gis.com/ru/api/search/get-started
"""
import requests
from django.conf import settings

DGIS_API_KEY = settings.DGIS_API_KEY
DGIS_BASE_URL = 'https://catalog.api.2gis.com/3.0'

# 2GIS kategoriya ID lari
CATEGORY_MAP = {
    'cafe': '164',        # Kafe, restoranlar
    'hotel': '179',       # Mehmonxonalar
    'museum': '183',      # Muzeylar
    'pharmacy': '149',    # Dorixonalar
    'atm': '178',         # ATM
}


def search_nearby(lat, lon, category='cafe', radius=1000, limit=10):
    """
    Berilgan koordinatalar atrofida joylarni qidirish.

    :param lat: Kenglik
    :param lon: Uzunlik
    :param category: Kategoriya (cafe, hotel, museum, pharmacy, atm)
    :param radius: Radius (metr)
    :param limit: Natijalar soni
    :return: list of dicts
    """
    if not DGIS_API_KEY:
        return []

    rubric_id = CATEGORY_MAP.get(category, '164')

    try:
        resp = requests.get(
            f"{DGIS_BASE_URL}/items",
            params={
                'key': DGIS_API_KEY,
                'q': '',
                'point': f"{lon},{lat}",
                'radius': radius,
                'rubric_id': rubric_id,
                'fields': 'items.point,items.address,items.contact_groups,items.reviews',
                'page_size': limit,
                'locale': 'uz_UZ',
            },
            timeout=10
        )

        if resp.status_code != 200:
            return []

        data = resp.json()
        items = data.get('result', {}).get('items', [])

        results = []
        for item in items:
            point = item.get('point', {})
            contacts = item.get('contact_groups', [])
            phone = ''
            if contacts:
                for group in contacts:
                    for contact in group.get('contacts', []):
                        if contact.get('type') == 'phone':
                            phone = contact.get('value', '')
                            break

            reviews = item.get('reviews', {})
            rating = reviews.get('rating', None)

            results.append({
                'external_id': item.get('id', ''),
                'name': item.get('name', ''),
                'address': item.get('address_name', ''),
                'latitude': point.get('lat', lat),
                'longitude': point.get('lon', lon),
                'phone': phone,
                'rating': rating,
                'category': category,
                'source': '2gis',
            })

        return results

    except Exception:
        return []


def get_map_key():
    """Frontend uchun 2GIS map kalitini qaytarish"""
    return DGIS_API_KEY