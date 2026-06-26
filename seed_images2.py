import os
import requests
from pathlib import Path

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from tours.models import Tour, TourImage
from regions.models import Region, Attraction

MEDIA_ROOT = Path('/app/media')

# Har bir obyekt uchun unique seed (har xil rasm chiqishi uchun)
tour_images = {
    'silk-road': [
        {'seed': 100, 'caption': 'Registon maydoni, Samarqand'},
        {'seed': 101, 'caption': 'Buxoro tarixiy markazi'},
        {'seed': 102, 'caption': 'Xiva Ichan-Qala'},
        {'seed': 103, 'caption': 'Toshkent shahri'},
    ],
    'classic-uzbekistan': [
        {'seed': 200, 'caption': 'O\'zbekiston me\'morligi'},
        {'seed': 201, 'caption': 'Samarqand masjidi'},
        {'seed': 202, 'caption': 'Buxoro qal\'asi'},
        {'seed': 203, 'caption': 'Xiva minoretasi'},
    ],
    '7-saints-of-bukhara': [
        {'seed': 300, 'caption': 'Buxoro sufiya merosi'},
        {'seed': 301, 'caption': 'O\'zbekiston masjidi'},
    ],
    'uzbekistan-samarkand': [
        {'seed': 400, 'caption': 'Ulug\'bek rasadxonasi'},
        {'seed': 401, 'caption': 'Shohizinda'},
    ],
}

region_images = {
    'toshkent': {'seed': 500, 'caption': 'Toshkent ko\'rinishi'},
    'samarqand': {'seed': 501, 'caption': 'Samarqand Registon'},
    'buxoro': {'seed': 502, 'caption': 'Buxoro eski shahar'},
    'xiva': {'seed': 503, 'caption': 'Xiva Ichan-Qala'},
    'fargona': {'seed': 504, 'caption': 'Farg\'ona vodiysi'},
}

attraction_images = {
    'Hazrati Imom majmuasi': 600,
    'Chorsu bozori': 601,
    'Barak-xana madrasasi': 602,
    'Toshkent teleminorasi': 603,
    'Amir Temur xiyoboni': 604,
    'Toshkent metrosi': 605,
    'Registon maydoni': 700,
    'Gur-Emir maqbarasi': 701,
    'Shohizinda': 702,
    'Ulug\'bek rasadxonasi': 703,
    'Bibi-Xonim masjidi': 704,
    'Siyob bozori': 705,
    'Po-i-Kalyan majmuasi': 800,
    'Ark qal\'asi': 801,
    'Somoniyalar maqbarasi': 802,
    'Bolo-Hovuz masjidi': 803,
    'Chashma Ayub': 804,
    'Ticorat gumbazlari': 805,
    'Ichan-Qala': 900,
    'Kalta-Minor minoretasi': 901,
    'Kunya-Ark qal\'asi': 902,
    'Juma masjidi': 903,
    'Tosh-Xovli saroyi': 904,
    'Islom-Xodji minoretasi': 905,
    'Marg\'ilon ipak fabrikasi': 1000,
    'Farg\'ona vodiyi tabiati': 1001,
    'Rishton kashtachilik': 1002,
    'Kokand hokimlik saroyi': 1003,
    'Shohimardon chashmasi': 1004,
    'Andijon tarixiy muzeyi': 1005,
}

def download_image(seed, save_path, width=800, height=600):
    """Picsum'dan rasm yuklab olish"""
    url = f'https://picsum.photos/seed/{seed}/{width}/{height}'
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
                if download_image(img_data['seed'], save_path):
                    TourImage.objects.get_or_create(
                        tour=tour,
                        caption=img_data['caption'],
                        defaults={'image': filename, 'order': i+1}
                    )
                    print(f'    OK: {filename}')
                else:
                    print(f'    Failed')
            else:
                # Fayl mavjud, lekin DB'da yo'q bo'lsa qo'shamiz
                obj, created = TourImage.objects.get_or_create(
                    tour=tour,
                    caption=img_data['caption'],
                    defaults={'image': filename, 'order': i+1}
                )
                if created:
                    print(f'  DB added: {filename}')
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
            if download_image(img_data['seed'], save_path):
                region.image = filename
                region.save()
                print(f'    OK: {filename}')
            else:
                print(f'    Failed')
        else:
            if not region.image:
                region.image = filename
                region.save()
            print(f'  Exists: {filename}')
    except Region.DoesNotExist:
        print(f'  Region not found: {region_slug}')

# ═══════ ATTRACTION RASMLARI ═══════
print('\n=== Attraction rasmlari ===')
for attraction in Attraction.objects.all():
    if attraction.name_uz in attraction_images:
        seed = attraction_images[attraction.name_uz]
        slug = attraction.name_uz.lower().replace(' ', '-').replace("'", '').replace("'", '')
        filename = f'attractions/{slug}.jpg'
        save_path = MEDIA_ROOT / filename
        if not save_path.exists() and not attraction.image:
            print(f'  Downloading: {attraction.name_uz}...')
            if download_image(seed, save_path):
                attraction.image = filename
                attraction.save()
                print(f'    OK: {filename}')
            else:
                print(f'    Failed')
        else:
            if not attraction.image:
                attraction.image = filename
                attraction.save()
            print(f'  Exists: {filename}')

print('\n=== Done ===')
print(f'Tours with images: {TourImage.objects.count()}')
print(f'Regions with images: {Region.objects.exclude(image="").count()}')
print(f'Attractions with images: {Attraction.objects.exclude(image="").count()}')
