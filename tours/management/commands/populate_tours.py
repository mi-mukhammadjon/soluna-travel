import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from regions.models import Region, Attraction
from tours.models import TourCategory, Tour


class Command(BaseCommand):
    help = "Baza uchun real va yuqori sifatli SoLuna turlarini shakllantirish"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Ma'lumotlarni shakllantirish boshlandi..."))

        # 1. Regionlarni tekshirish va yaratish
        tashkent_reg, _ = Region.objects.get_or_create(name="Tashkent", defaults={"slug": "tashkent"})
        samarkand_reg, _ = Region.objects.get_or_create(name="Samarkand", defaults={"slug": "samarkand"})
        bukhara_reg, _ = Region.objects.get_or_create(name="Bukhara", defaults={"slug": "bukhara"})
        khiva_reg, _ = Region.objects.get_or_create(name="Khorezm (Khiva)", defaults={"slug": "khiva"})

        # 2. Attraksionlarni yaratish (Slug maydoni olib tashlandi)
        registan, _ = Attraction.objects.get_or_create(name="Registan Square", region=samarkand_reg)
        ark, _ = Attraction.objects.get_or_create(name="Ark Citadel", region=bukhara_reg)
        ichan_kala, _ = Attraction.objects.get_or_create(name="Ichan Kala", region=khiva_reg)
        chimgan, _ = Attraction.objects.get_or_create(name="Amirsoy & Chimgan Mountains", region=tashkent_reg)

        # 3. Kategoriyalarni yaratish
        cat_cultural, _ = TourCategory.objects.get_or_create(
            slug="cultural-historical",
            defaults={"name": "Cultural & Historical", "icon": "fa-landmark"}
        )
        cat_nature, _ = TourCategory.objects.get_or_create(
            slug="nature-adventure",
            defaults={"name": "Nature & Adventure", "icon": "fa-mountain"}
        )

        # ----------------------------------------------------------------
        # TOUR 1: Mistik Ipak Yo'li Bo'ylab (7 kunlik madaniy tur)
        # ----------------------------------------------------------------
        tour1_title = "Heart of the Silk Road: Tashkent, Samarkand & Bukhara"
        tour1_slug = slugify(tour1_title)
        
        itinerary1 = [
            {
                "day": 1,
                "title": "Arrival in Tashkent",
                "content": "Meet your guide at Tashkent International Airport. Transfer to hotel. Afternoon city tour exploring Khazrati Imam Complex and Chorsu Bazaar."
            },
            {
                "day": 2,
                "title": "High-Speed Train to Samarkand",
                "content": "Morning departure via Afrosiyob train. Check-in at hotel. Visit the magnificent Registan Square and Gur-Emir Mausoleum."
            },
            {
                "day": 3,
                "title": "Samarkand Deep Dive",
                "content": "Discover Bibi-Khanym Mosque, Shah-i-Zinda Necropolis, and the ancient Ulugh Beg Observatory. Evening free for leisure."
            },
            {
                "day": 4,
                "title": "Journey to Holy Bukhara",
                "content": "Travel to Bukhara by train. Check-in and evening walk around the iconic Lyabi-Khauz ensemble with traditional tea tasting."
            },
            {
                "day": 5,
                "title": "Bukhara Ancient Architecture",
                "content": "Full day walking tour: Ark Citadel, Bolo Hauz Mosque, Kalyan Minaret, and the historic Trading Domes."
            },
            {
                "day": 6,
                "title": "Sitorai Mokhi-Khosa & Return",
                "content": "Visit the summer residence of the last Emir of Bukhara. Afternoon train back to Tashkent. Farewell dinner."
            },
            {
                "day": 7,
                "title": "Departure",
                "content": "Transfer to Tashkent International Airport for your flight back home. End of SoLuna services."
            }
        ]

        tour1, created1 = Tour.objects.get_or_create(
            slug=tour1_slug,
            defaults={
                "title": tour1_title,
                "category": cat_cultural,
                "description": "Embark on an unforgettable journey through Uzbekistan's most iconic oasis cities. This tour is designed to unveil the rich tapestry of history, majestic architecture, and vibrant traditions that defined the ancient Silk Road trading routes.",
                "short_description": "Discover the timeless heritage of Uzbekistan's majestic Silk Road oases in a premium 7-day guided experience.",
                "price": Decimal("850.00"),
                "price_uzs": Decimal("10800000.00"),
                "duration_days": 7,
                "max_group_size": 12,
                "difficulty": "easy",
                "includes": "AC Transportation\nHigh-speed train tickets (Afrosiyob)\n3-4 star hotel accommodation with breakfast\nProfessional English/Russian speaking guide\nEntering tickets to all historical monuments\nWelcome and farewell dinners",
                "excludes": "International flights\nPersonal expenses\nTips for guides and drivers\nSingle room supplement fee",
                "itinerary": itinerary1,
                "is_active": True,
                "is_featured": True,
            }
        )
        if created1:
            tour1.regions.add(tashkent_reg, samarkand_reg, bukhara_reg)
            tour1.attractions.add(registan, ark)
            self.stdout.write(self.style.SUCCESS(f"Yaratildi: {tour1_title}"))

        # ----------------------------------------------------------------
        # TOUR 2: Amirsoy va Tyan-Shan Tog'lari (3 kunlik tabiat turi)
        # ----------------------------------------------------------------
        tour2_title = "Tian Shan Escape: Amirsoy & Charvak Adventure"
        tour2_slug = slugify(tour2_title)

        itinerary2 = [
            {
                "day": 1,
                "title": "Tashkent to Amirsoy Resort",
                "content": "Scenic drive to the Tian Shan mountains. Check-in at the mountain resort. Take the cable car to the peak (2290m) for panoramic views."
            },
            {
                "day": 2,
                "title": "Hiking & Charvak Lake Relaxation",
                "content": "Guided morning hike along the picturesque eco-trails. Afternoon transfer to Charvak Lake for optional paragliding, jet ski, or lakeside relaxation."
            },
            {
                "day": 3,
                "title": "Gulkam Canyons & Return",
                "content": "Short trek to the beautiful Gulkam waterfalls and narrow canyon passes. Afternoon traditional mountain lunch before returning to Tashkent."
            }
        ]

        tour2, created2 = Tour.objects.get_or_create(
            slug=tour2_slug,
            defaults={
                "title": tour2_title,
                "category": cat_nature,
                "description": "Escape the city buzz and breathe the crisp mountain air of the Western Tian Shan range. Experience world-class infrastructure at Amirsoy, paired with raw natural beauty, trekking trails, and the turquoise waters of Charvak reservoir.",
                "short_description": "A perfect 3-day mountain getaway exploring Amirsoy peaks and Charvak lake with light trekking.",
                "price": Decimal("320.00"),
                "price_uzs": Decimal("4050000.00"),
                "duration_days": 3,
                "max_group_size": 15,
                "difficulty": "medium",
                "includes": "Comfortable 4x4 or Minivan transport\n2 nights accommodation in a mountain chalet\nAll meals (Breakfast, Lunch, Dinner)\nCable car passes at Amirsoy\nCertified mountain trekking guide",
                "excludes": "Paragliding fees\nWater sports activities on Charvak\nAlcoholic beverages\nInsurance",
                "itinerary": itinerary2,
                "is_active": True,
                "is_featured": False,
            }
        )
        if created2:
            tour2.regions.add(tashkent_reg)
            tour2.attractions.add(chimgan)
            self.stdout.write(self.style.SUCCESS(f"Yaratildi: {tour2_title}"))

        # ----------------------------------------------------------------
        # TOUR 3: Xiva va Orol Dengizi Ekspeditsiyasi (5 kunlik sarguzasht)
        # ----------------------------------------------------------------
        tour3_title = "Khiva Oasis & Aral Sea Desert Expedition"
        tour3_slug = slugify(tour3_title)

        itinerary3 = [
            {
                "day": 1,
                "title": "Welcome to Open-Air Museum Khiva",
                "content": "Fly from Tashkent to Urgench, transfer to Khiva. Afternoon tour of Ichan-Kala: Kalta Minor, Kunya-Ark, and Islam Khodja Minaret."
            },
            {
                "day": 2,
                "title": "Khiva to Nukus via Ancient Fortresses",
                "content": "Drive through the Kyzylkum desert visiting ancient fortresses of Khwarezm: Ayaz-Kala and Toprak-Kala. Overnight in Nukus."
            },
            {
                "day": 3,
                "title": "Journey to the Edge of Aral Sea",
                "content": "4x4 expedition via Kungrad to the Ustyurt Plateau. Descent to the shore of the Aral Sea. Night in a traditional yurt camp under the stars."
            },
            {
                "day": 4,
                "title": "Muynak Ship Graveyard & Savitsky Museum",
                "content": "Morning sunrise over the sea. Drive to Muynak to see the former port and Ship Graveyard. Return to Nukus to visit the famous Savitsky Avant-Garde Museum."
            },
            {
                "day": 5,
                "title": "Return Flight to Tashkent",
                "content": "Transfer to Nukus Airport for your flight back to Tashkent. Wrap up your extreme desert experience."
            }
        ]

        tour3, created3 = Tour.objects.get_or_create(
            slug=tour3_slug,
            defaults={
                "title": tour3_title,
                "category": cat_cultural,
                "description": "A thrilling blend of living history and extreme ecological expedition. Explore the preserved medieval streets of Khiva, cross the harsh Kyzylkum desert in 4x4 vehicles, witness the dramatic history of the Aral Sea at Muynak, and sleep under a blanket of stars in a remote yurt camp.",
                "short_description": "An off-road 5-day expedition combining the fairy tale of Khiva with the dramatic Aral Sea landscapes.",
                "price": Decimal("690.00"),
                "price_uzs": Decimal("8750000.00"),
                "duration_days": 5,
                "max_group_size": 8,
                "difficulty": "hard",
                "includes": "Internal domestic flights (Tashkent-Urgench, Nukus-Tashkent)\nProfessional 4x4 off-road vehicles with experienced drivers\nHotels and 1 night stay in an authentic desert Yurt Camp\nFull-board meals during the desert expedition\nLocal expert guides and museum entry fees",
                "excludes": "Tips for drivers\nPersonal gears\nSoft and energy drinks",
                "itinerary": itinerary3,
                "is_active": True,
                "is_featured": True,
            }
        )
        if created3:
            tour3.regions.add(khiva_reg)
            tour3.attractions.add(ichan_kala)
            self.stdout.write(self.style.SUCCESS(f"Yaratildi: {tour3_title}"))

        self.stdout.write(self.style.SUCCESS("Barcha turlar muvaffaqiyatli bazaga yuklandi!"))