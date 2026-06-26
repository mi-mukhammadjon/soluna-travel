import os
import requests
from pathlib import Path

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from tours.models import Tour, TourImage
from regions.models import Region, Attraction

MEDIA_ROOT = Path('/app/media')

# Tour rasmlari uchun Unsplash search query
tour_images = {
    'silk-road': [
        {'query': 'samarkand registan', 'caption': 'Registon maydoni, Samarqand'},
        {'query': 'bukhara uzbekistan', 'caption': 'Buxoro tarixiy markazi'},
        {'query': 'khiva uzbekistan', 'caption': 'Xiva Ichan-Qala'},
        {'query': 'tashkent uzbekistan', 'caption': 'Toshkent shahri'},
    ],
    'classic-uzbekistan': [
        {'query': 'uzbekistan architecture', 'caption': 'O\'zbekiston me\'morligi'},
        {'query': 'samarkand mosque', 'caption': 'Samarqand masjidi'},
        {'query': 'bukhara fortress', 'caption': 'Buxoro qal\'asi'},
        {'query': 'khiva minaret', 'caption': 'Xiva minoretasi'},
    ],
    '7-saints-of-bukhara': [
        {'query': 'bukhara sufi', 'caption': 'Buxoro sufiya merosi'},
        {'query': 'uzbekistan mosque', 'caption': 'O\'zbekiston masjidi'},
    ],
    'uzbekistan-samarkand': [
        {'query': 'samarkand ulugh beg', 'caption': 'Ulug\'bek rasadxonasi'},
        {'query': 'shah-i-zinda samarkand', 'caption': 'Shohizinda'},
    ],
}

# Region rasmlari
region_images = {
    'toshkent': {'query': 'tashkent skyline', 'caption': 'Toshkent ko\'rinishi'},
    'samarqand': {'query': 'samarkand registan', 'caption': 'Samarqand Registon'},
    'buxoro': {'query': 'bukhara old city', 'caption': 'Buxoro eski shahar'},
    'xiva': {'query': 'khiva ichan kala', 'caption': 'Xiva Ichan-Qala'},
    'fargona': {'query': 'fergana valley uzbekistan', 'caption': 'Farg\'ona vodiysi'},
}

# Attraction rasmlari
attraction_images = {
    'Hazrati Imom majmuasi': 'tashkent hast imam',
    'Chorsu bozori': 'tashkent bazaar',
    'Barak-xana madrasasi': 'tashkent madrasa',
    'Toshkent teleminorasi': 'tashkent tower',
    'Amir Temur xiyoboni': 'amir timur statue tashkent',
    'Toshkent metrosi': 'tashkent metro station',
    'Registon maydoni': 'registan samarkand',
    'Gur-Emir maqbarasi': 'gur emir samarkand',
    'Shohizinda': 'shah i zinda samarkand',
    'Ulug\'bek rasadxonasi': 'ulugh beg observatory',
    'Bibi-Xonim masjidi': 'bibi khanym mosque',
    'Siyob bozori': 'siyab bazaar samarkand',
    'Po-i-Kalyan majmuasi': 'po i kalyan bukhara',
    'Ark qal\'asi': 'ark fortress bukhara',
    'Somoniyalar maqbarasi': 'samanid mausoleum bukhara',
    'Bolo-Hovuz masjidi': 'bolo khauz mosque bukhara',
    'Chashma Ayub': 'chashma ayub bukhara',
    'Ticorat gumbazlari': 'trading domes bukhara',
    'Ichan-Qala': 'ichan kala khiva',
    'Kalta-Minor minoretasi': 'kalta minor khiva',
    'Kunya-Ark qal\'asi': 'kunya ark khiva',
    'Juma masjidi': 'juma mosque khiva',
    'Tosh-Xovli saroyi': 'tash khovli palace khiva',
    'Islom-Xodji minoretasi': 'islam khoja minaret khiva',
    'Marg\'ilon ipak fabrikasi': 'margilan silk factory',
    'Farg\'ona vodiyi tabiati': 'fergana valley nature',
    'Rishton kashtachilik': 'rishton ceramics uzbekistan',
    'Kokand hokimlik saroyi': 'khudoyar khan palace',
    'Shohimardon chashmasi': 'shahimardon spring',
    'Andijon tarixiy muzeyi': 'andijan museum',
}

def download_image(query, save_path, width=800, height=600):
    """Unsplash'dan rasm yuklab olish"""
    url = f'https://source.unsplash.com/{width}x{height}/?{query}'
    try:
        response = requests.get(url, timeout=15, allow_redirects=True)
        if response.status_code == 200 and len(response.content) > 1000:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f'    Error: {e}')
    return False

# ═══════ TOUR RASMLARI ═══════
print('=== Tour rasmlari ===')
for tour_slug, images in tour_images.items():
    try:
        tour = Tour.objects.get(slug=tour_slug)
        for i, img_data in enumerate(images):
            filename = f'tours/{tour_slug}_{i+1}.jpg'
            save_path = MEDIA_ROOT / filename
            if not save_path.exists():
                print(f'  Downloading: {img_data["caption"]}...')
                if download_image(img_data['query'], save_path):
                    TourImage.objects.get_or_create(
                        tour=tour,
                        caption=img_data['caption'],
                        defaults={'image': filename, 'order': i+1}
                    )
                    print(f'    OK: {filename}')
                else:
                    print(f'    Failed: {img_data["caption"]}')
            else:
                print(f'  Exists: {filename}')
    except Tour.DoesNotExist:
        print(f'  Tour not found: {tour_slug}')

# ═══════ REGION RASMLARI ═══════
print('\n=== Region rasmlari ===')
for region_slug, img_data in region_images.items():
    try:
        region = Region.objects.get(slug=region_slug)
        filename = f'regions/{region_slug}.jpg'
        save_path = MEDIA_ROOT / filename
        if not save_path.exists() and not region.image:
            print(f'  Downloading: {img_data["caption"]}...')
            if download_image(img_data['query'], save_path):
                region.image = filename
                region.save()
                print(f'    OK: {filename}')
            else:
                print(f'    Failed')
        else:
            print(f'  Exists: {filename}')
    except Region.DoesNotExist:
        print(f'  Region not found: {region_slug}')

# ═══════ ATTRACTION RASMLARI ═══════
print('\n=== Attraction rasmlari ===')
for attraction in Attraction.objects.all():
    if attraction.name_uz in attraction_images:
        query = attraction_images[attraction.name_uz]
        slug = attraction.name_uz.lower().replace(' ', '-').replace("'", '').replace("'", '')
        filename = f'attractions/{slug}.jpg'
        save_path = MEDIA_ROOT / filename
        if not save_path.exists() and not attraction.image:
            print(f'  Downloading: {attraction.name_uz}...')
            if download_image(query, save_path):
                attraction.image = filename
                attraction.save()
                print(f'    OK: {filename}')
            else:
                print(f'    Failed')
        else:
            print(f'  Exists: {filename}')

print('\n=== Done ===')
print(f'Tours with images: {TourImage.objects.count()}')
print(f'Regions with images: {Region.objects.exclude(image="").count()}')
print(f'Attractions with images: {Attraction.objects.exclude(image="").count()}')
