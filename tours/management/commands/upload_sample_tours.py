"""
upload_sample_tours — production seeder.

`media/sample/` papkasidagi 3 ta real turni (Ipak yo'li, Klassik O'zbekiston,
Buxoroning 7 piri) PRODUCTION sifatida bazaga yuklaydi:

  • Barcha matnlar 9 tilda tarjima qilingan (uz, ru, en, zh-hans, ar, de, fr, ja, ko)
  • Regionlar va ularning diqqatga sazovor joylari (aniq lat/lng koordinatalar bilan)
  • Har bir diqqatga sazovor joy uchun "nearby" joylar (hotel/kafe/muzey/ATM ...)
  • Higgsfield (soul_2) orqali har bir region/turga moslab yaratilgan rasmlar
    (seed_assets/ papkasidan biriktiriladi)

Ma'lumotning o'zi  _sample_tours_data.py  faylida turadi.

Ishlatish:
    docker compose exec web python manage.py upload_sample_tours
    docker compose exec web python manage.py upload_sample_tours --no-images
    docker compose exec web python manage.py upload_sample_tours --force-images
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from regions.models import Region, Attraction
from places.models import NearbyPlace
from tours.models import Tour, TourCategory, ItineraryDay, TourImage

from ._sample_tours_data import (
    LANGS,
    CATEGORIES,
    REGIONS,
    ATTRACTIONS,
    NEARBY_PLACES,
    TOURS,
)

# Seed rasmlari repo ichida — `media` named volume `.:/app` ni soyalagani uchun
# bu papka media/ ichida EMAS (aks holda konteynerda ko'rinmaydi).
SEED_DIR = Path(settings.BASE_DIR) / "seed_assets"


# ──────────────────────────────────────────────────────────────────────────
#  Yordamchi funksiyalar
# ──────────────────────────────────────────────────────────────────────────
def set_i18n(obj, field, values):
    """`values` = {'uz': '...', 'ru': '...', ...}  ->  obj.field_<lang> = value.

    Berilmagan tillar uchun modeltranslation fallback (uz→ru→en) ishlaydi,
    shuning uchun hech bo'lmaganda uz/ru/en to'ldirilgan bo'lishi shart.
    """
    if not values:
        return
    # Asosiy (tarjimasiz) ustun ham to'lsin — odatda uz qiymati
    base = values.get("uz") or values.get("en") or next(iter(values.values()))
    setattr(obj, field, base)
    for lang in LANGS:
        if values.get(lang):
            setattr(obj, f"{field}_{lang}", values[lang])


def attach_image(obj, field, rel_path, *, force=False, stdout=None):
    """media/seed/<rel_path> faylini ImageField'ga biriktiradi.

    Fayl bo'lmasa — jim o'tib ketadi (script har doim ishlayveradi).
    `force=False` bo'lsa va rasm allaqachon o'rnatilgan bo'lsa — qayta yozmaydi.
    """
    path = SEED_DIR / rel_path
    if not path.exists():
        if stdout:
            stdout.write(f"   · rasm topilmadi (o'tkazib yuborildi): seed/{rel_path}")
        return False
    current = getattr(obj, field)
    if current and not force:
        return False
    with path.open("rb") as fh:
        getattr(obj, field).save(path.name, File(fh), save=True)
    if stdout:
        stdout.write(f"   ✓ rasm biriktirildi: seed/{rel_path}")
    return True


class Command(BaseCommand):
    help = "media/sample/ turlarini 9 tilda, rasm va nearby joylari bilan yuklaydi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-images", action="store_true",
            help="Rasmlarni biriktirmaslik (faqat matn ma'lumotlari).",
        )
        parser.add_argument(
            "--force-images", action="store_true",
            help="Allaqachon o'rnatilgan rasmlarni ham qayta yozish.",
        )

    # ──────────────────────────────────────────────────────────────────
    @transaction.atomic
    def handle(self, *args, **opts):
        self.with_images = not opts["no_images"]
        self.force_images = opts["force_images"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n═══ 1/5  Kategoriyalar ═══"))
        self.cats = self._seed_categories()

        self.stdout.write(self.style.MIGRATE_HEADING("\n═══ 2/5  Regionlar ═══"))
        self.regions = self._seed_regions()

        self.stdout.write(self.style.MIGRATE_HEADING("\n═══ 3/5  Diqqatga sazovor joylar ═══"))
        self.attractions = self._seed_attractions()

        self.stdout.write(self.style.MIGRATE_HEADING("\n═══ 4/5  Nearby joylar ═══"))
        self._seed_nearby()

        self.stdout.write(self.style.MIGRATE_HEADING("\n═══ 5/5  Turlar ═══"))
        self._seed_tours()

        self.stdout.write(self.style.SUCCESS("\n✅ Tayyor — barcha ma'lumotlar yuklandi.\n"))

    # ──────────────────────────────────────────────────────────────────
    def _seed_categories(self):
        out = {}
        for data in CATEGORIES:
            cat, _ = TourCategory.objects.get_or_create(slug=data["slug"])
            set_i18n(cat, "name", data["name"])
            cat.icon = data.get("icon", cat.icon)
            cat.save()
            out[data["slug"]] = cat
            self.stdout.write(f" • {cat.name_uz}")
        return out

    def _seed_regions(self):
        out = {}
        for data in REGIONS:
            region, _ = Region.objects.get_or_create(slug=data["slug"])
            set_i18n(region, "name", data["name"])
            set_i18n(region, "description", data["description"])
            region.order = data.get("order", region.order)
            region.is_active = True
            region.save()
            if self.with_images and data.get("image"):
                attach_image(region, "image", data["image"],
                             force=self.force_images, stdout=self.stdout)
            out[data["slug"]] = region
            self.stdout.write(f" • {region.name_uz}")
        return out

    def _seed_attractions(self):
        out = {}
        for data in ATTRACTIONS:
            region = self.regions[data["region"]]
            # Bir region ichida nom bo'yicha topamiz (idempotent)
            attr = (Attraction.objects
                    .filter(region=region, name_uz=data["name"]["uz"]).first())
            if attr is None:
                attr = Attraction(region=region)
            set_i18n(attr, "name", data["name"])
            set_i18n(attr, "description", data["description"])
            attr.latitude = data["lat"]
            attr.longitude = data["lng"]
            attr.order = data.get("order", 0)
            attr.is_active = True
            attr.save()
            if self.with_images and data.get("image"):
                attach_image(attr, "image", data["image"],
                             force=self.force_images, stdout=self.stdout)
            out[data["key"]] = attr
            self.stdout.write(f" • {region.name_uz} → {attr.name_uz}")
        return out

    def _seed_nearby(self):
        for data in NEARBY_PLACES:
            attr = self.attractions.get(data["attraction"])
            if attr is None:
                continue
            NearbyPlace.objects.update_or_create(
                attraction=attr,
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "address": data.get("address", ""),
                    "latitude": data["lat"],
                    "longitude": data["lng"],
                    "phone": data.get("phone", ""),
                    "website": data.get("website", ""),
                    "rating": data.get("rating"),
                    "source": data.get("source", "2gis"),
                    "is_active": True,
                },
            )
            self.stdout.write(f" • {attr.name_uz} ↳ {data['name']}")

    def _seed_tours(self):
        for data in TOURS:
            tour, _ = Tour.objects.get_or_create(
                slug=data["slug"],
                defaults={"price": data["price"], "duration_days": data["duration_days"]},
            )
            set_i18n(tour, "title", data["title"])
            set_i18n(tour, "short_description", data["short_description"])
            set_i18n(tour, "description", data["description"])
            set_i18n(tour, "includes", data["includes"])
            set_i18n(tour, "excludes", data["excludes"])

            tour.category = self.cats[data["category"]]
            tour.price = data["price"]
            tour.price_uzs = data.get("price_uzs")
            tour.duration_days = data["duration_days"]
            tour.max_group_size = data.get("max_group_size", 15)
            tour.difficulty = data.get("difficulty", "easy")
            tour.is_active = True
            tour.is_featured = data.get("is_featured", False)
            tour.is_recommended = data.get("is_recommended", False)
            tour.save()

            # Regionlar va diqqatga sazovor joylar
            tour.regions.set([self.regions[s] for s in data["regions"]])
            tour.attractions.set(
                [self.attractions[k] for k in data.get("attractions", [])
                 if k in self.attractions]
            )

            # Cover + galereya rasmlari
            if self.with_images:
                attach_image(tour, "cover_image", data["cover_image"],
                             force=self.force_images, stdout=self.stdout)
                self._seed_gallery(tour, data.get("gallery", []))

            # Kun-ba-kun dastur (9 tilda)
            self._seed_itinerary(tour, data.get("itinerary", []))

            self.stdout.write(self.style.SUCCESS(f" ✔ {tour.title_uz}  ({tour.price}$)"))

    def _seed_gallery(self, tour, gallery):
        for i, item in enumerate(gallery):
            path = SEED_DIR / item["image"]
            if not path.exists():
                continue
            img, created = TourImage.objects.get_or_create(tour=tour, order=i)
            img.caption = item.get("caption_uz", "")
            if self.force_images or not img.image:
                with path.open("rb") as fh:
                    img.image.save(path.name, File(fh), save=True)

    def _seed_itinerary(self, tour, itinerary):
        # Eski kunlarni tozalab, qayta yozamiz (idempotent)
        tour.days.all().delete()
        json_days = []
        for d in itinerary:
            day = ItineraryDay(tour=tour, day=d["day"])
            set_i18n(day, "title", d["title"])
            set_i18n(day, "description", d["description"])
            day.save()
            json_days.append({
                "day": d["day"],
                "title": d["title"].get("uz", ""),
                "description": d["description"].get("uz", ""),
            })
        # Tour.itinerary JSONField (tarjimali) — har til uchun ro'yxat
        for lang in LANGS:
            value = [{
                "day": d["day"],
                "title": d["title"].get(lang) or d["title"].get("uz", ""),
                "description": d["description"].get(lang) or d["description"].get("uz", ""),
            } for d in itinerary]
            setattr(tour, f"itinerary_{lang}", value)
        tour.itinerary = json_days
        tour.save(update_fields=["itinerary"] + [f"itinerary_{l}" for l in LANGS])
