"""
Tour itinerary (kunma-kun dastur)larni DBga yozadi.

Joylash: tours/management/commands/seed_tour_itineraries.py

Ishlatish:
  docker compose exec web python manage.py seed_tour_itineraries

ESLATMA: Avval `seed_real_tours` ishlatilgan bo'lishi kerak.
Tour modelida itinerary uchun related model bo'lishi kerak (ItineraryDay yoki shunga o'xshash).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps


# ════════════════════════════════════════════════════════════════════
# ITINERARIES — har bir tur uchun kunma-kun dastur
# ════════════════════════════════════════════════════════════════════
ITINERARIES = {

    # ── Tour 1: TAS-SAM-BUK 8 kun ───────────────────────────────────
    "uzbekistan-tashkent-samarkand-bukhara-8d": [
        {
            "day": 1,
            "title_uz": "Toshkentga kelish",
            "title_ru": "Прибытие в Ташкент",
            "title_en": "Arrival in Tashkent",
            "title_ko": "타슈켄트 도착",
            "description_uz": "Aeroportda kutib olish, mehmonxonaga transfer. 14:00 dan keyin joylashish. Bo'sh vaqt. Toshkentda tunash.",
            "description_ru": "Встреча в аэропорту, трансфер в отель. Размещение после 14:00. Свободное время. Ночь в Ташкенте.",
            "description_en": "Airport pickup, transfer to hotel. Check-in after 14:00. Free time. Overnight in Tashkent.",
            "description_ko": "공항 픽업, 호텔로 트랜스퍼. 14:00 이후 체크인. 자유시간. 타슈켄트에서 숙박.",
        },
        {
            "day": 2,
            "title_uz": "Toshkent ekskursiyasi",
            "title_ru": "Экскурсия по Ташкенту",
            "title_en": "Tashkent City Tour",
            "title_ko": "타슈켄트 시티 투어",
            "description_uz": "Nonushta. Toshkent bo'ylab ekskursiya: Xast-Imom maydoni, Baroqxon madrasasi, Tilla-Shayx masjidi, Chorsu bozori, Mustaqillik maydoni, Amir Temur xiyoboni. Toshkentda tunash.",
            "description_ru": "Завтрак. Экскурсия: площадь Хаст-Имам, медресе Баракхан, мечеть Тилля-Шейх, базар Чорсу, площадь Независимости, сквер Амира Темура. Ночь в Ташкенте.",
            "description_en": "Breakfast. Sightseeing: Khast-Imam square, Barak-Khan madrasah, Tilla-Sheikh mosque, Chorsu bazaar, Independence Square, Amir Temur square. Overnight in Tashkent.",
            "description_ko": "조식. 관광: 하스트이맘 광장, 바라크칸 마드라사, 틸라셰이크 모스크, 초르수 시장, 독립광장, 아미르 티무르 광장. 타슈켄트 숙박.",
        },
        {
            "day": 3,
            "title_uz": "Toshkent → Samarqand",
            "title_ru": "Ташкент → Самарканд",
            "title_en": "Tashkent → Samarkand",
            "title_ko": "타슈켄트 → 사마르칸트",
            "description_uz": "Nonushta. Afrosiyob tezyurar poyezdida Samarqandga. Joylashish. Registon maydoni va Go'ri Amir maqbarasi. Samarqandda tunash.",
            "description_ru": "Завтрак. Скоростной поезд «Афросиаб» в Самарканд. Размещение. Площадь Регистан, мавзолей Гур-Эмир. Ночь в Самарканде.",
            "description_en": "Breakfast. Afrosiyob high-speed train to Samarkand. Check-in. Registan Square, Gur-e-Amir mausoleum. Overnight in Samarkand.",
            "description_ko": "조식. 아프로시얍 고속열차로 사마르칸트행. 체크인. 레기스탄 광장, 구르 에미르 영묘. 사마르칸트 숙박.",
        },
        {
            "day": 4,
            "title_uz": "Samarqand ekskursiyasi",
            "title_ru": "Экскурсия по Самарканду",
            "title_en": "Samarkand Sightseeing",
            "title_ko": "사마르칸트 관광",
            "description_uz": "Nonushta. Bibi-Xonim masjidi, Siyob bozori, Shohi-Zinda nekropoli, Ulug'bek rasadxonasi. Samarqandda tunash.",
            "description_ru": "Завтрак. Мечеть Биби-Ханым, Сиабский базар, некрополь Шахи-Зинда, обсерватория Улугбека. Ночь в Самарканде.",
            "description_en": "Breakfast. Bibi-Khanym mosque, Siab bazaar, Shah-i-Zinda necropolis, Ulugh Beg observatory. Overnight in Samarkand.",
            "description_ko": "조식. 비비하늠 모스크, 시압 시장, 샤히진다 네크로폴리스, 울루그벡 천문대. 사마르칸트 숙박.",
        },
        {
            "day": 5,
            "title_uz": "Samarqand → Buxoro",
            "title_ru": "Самарканд → Бухара",
            "title_en": "Samarkand → Bukhara",
            "title_ko": "사마르칸트 → 부하라",
            "description_uz": "Nonushta. Poyezdda Buxoroga. Joylashish. Eski shahar bo'ylab ekskursiya: Labi-Hovuz ansambli, Ko'kaldosh madrasasi, savdo gumbazlari. Buxoroda tunash.",
            "description_ru": "Завтрак. Поезд в Бухару. Размещение. Экскурсия по Старому городу: ансамбль Ляби-Хауз, медресе Кукельдаш, торговые купола. Ночь в Бухаре.",
            "description_en": "Breakfast. Train to Bukhara. Check-in. Old city tour: Lyab-i-Hauz ensemble, Kukeldash madrasah, trading domes. Overnight in Bukhara.",
            "description_ko": "조식. 부하라행 기차. 체크인. 구시가지 투어: 라비하우즈 단지, 쿠켈다시 마드라사, 무역 돔. 부하라 숙박.",
        },
        {
            "day": 6,
            "title_uz": "Buxoro to'liq kuni",
            "title_ru": "Полный день в Бухаре",
            "title_en": "Full day in Bukhara",
            "title_ko": "부하라 종일 투어",
            "description_uz": "Nonushta. To'liq kun ekskursiya: Ark qal'asi, Bolo-Hovuz masjidi, Po'i-Kalon majmuasi, Somoniylar maqbarasi, Chashma-Ayub. Buxoroda tunash.",
            "description_ru": "Завтрак. Полный день экскурсий: крепость Арк, мечеть Боло-Хауз, комплекс Пои-Калян, мавзолей Саманидов, Чашма-Аюб. Ночь в Бухаре.",
            "description_en": "Breakfast. Full day sightseeing: Ark fortress, Bolo-Hauz mosque, Poi-Kalyan complex, Samanid mausoleum, Chashma-Ayub. Overnight in Bukhara.",
            "description_ko": "조식. 종일 관광: 아르크 요새, 볼로하우즈 모스크, 포이칼란 단지, 사마니드 영묘, 차슈마-아유브. 부하라 숙박.",
        },
        {
            "day": 7,
            "title_uz": "Buxoro → Toshkent",
            "title_ru": "Бухара → Ташкент",
            "title_en": "Bukhara → Tashkent",
            "title_ko": "부하라 → 타슈켄트",
            "description_uz": "Nonushta. Tezyurar poyezdda Toshkentga. Joylashish. Sayrlar, xaridlar va milliy taomlar uchun bo'sh vaqt. Toshkentda tunash.",
            "description_ru": "Завтрак. Утренний переезд на скоростном поезде в Ташкент. Размещение. Свободное время для прогулок, шопинга и национальной кухни. Ночь в Ташкенте.",
            "description_en": "Breakfast. Morning high-speed train to Tashkent. Check-in. Free time for walking, shopping, and local cuisine. Overnight in Tashkent.",
            "description_ko": "조식. 오전 고속열차로 타슈켄트행. 체크인. 산책, 쇼핑, 현지 음식 즐기는 자유시간. 타슈켄트 숙박.",
        },
        {
            "day": 8,
            "title_uz": "Jo'nash",
            "title_ru": "Вылет",
            "title_en": "Departure",
            "title_ko": "출발",
            "description_uz": "Nonushta. 12:00 gacha xona bo'shatish. Xalqaro aeroportga transfer. Uchish.",
            "description_ru": "Завтрак. Освобождение номеров до 12:00. Трансфер в международный аэропорт. Вылет.",
            "description_en": "Breakfast. Check-out by 12:00. Transfer to international airport. Departure.",
            "description_ko": "조식. 12:00까지 체크아웃. 국제공항 트랜스퍼. 출발.",
        },
    ],

    # ── Tour 2: ARAL 3 kun ──────────────────────────────────────────
    "aral-sea-3d-adventure": [
        {
            "day": 1,
            "title_uz": "Toshkent ✈ Nukus – Mo'ynoq – Ustyurt – Orol (jip-tur)",
            "title_ru": "Ташкент ✈ Нукус – Муйнак – Устюрт – Арал (джип-тур)",
            "title_en": "Tashkent ✈ Nukus – Moynaq – Ustyurt – Aral (jeep tour)",
            "title_ko": "타슈켄트 ✈ 누쿠스 – 모이낙 – 우스튜르트 – 아랄 (지프 투어)",
            "description_uz": "Aeroportga transfer va Nukusga ichki reys. Orol dengizining ekologik halokat zonasiga 450 km, 8 soatlik sayohat. Mo'ynoq — kemalar qabristoni va muzey. Tushlik. Ustyurt platosi kanyoni. Yurtada kechki ovqat va tunash.",
            "description_ru": "Трансфер в аэропорт и внутренний рейс в Нукус. Путь к зоне экологической катастрофы — 450 км, 8 часов. Муйнак — кладбище кораблей и музей. Обед. Каньон плато Устюрт. Ужин и ночёвка в юрте.",
            "description_en": "Airport transfer and domestic flight to Nukus. Journey to ecological disaster zone — 450 km, 8 hours. Moynaq — ship cemetery and museum. Lunch. Ustyurt plateau canyon. Dinner and overnight in yurt camp.",
            "description_ko": "공항 트랜스퍼와 누쿠스행 국내선. 생태 재앙 지역으로 450km, 8시간 여정. 모이낙 — 선박 묘지와 박물관. 중식. 우스튜르트 고원 협곡. 유르트 캠프에서 석식과 숙박.",
        },
        {
            "day": 2,
            "title_uz": "Orol – Sudochye – Mizdaxkon – Nukus ✈ Toshkent",
            "title_ru": "Арал – Судочье – Миздахкан – Нукус ✈ Ташкент",
            "title_en": "Aral – Sudochie – Mizdakhan – Nukus ✈ Tashkent",
            "title_ko": "아랄 – 수도치에 – 미즈다칸 – 누쿠스 ✈ 타슈켄트",
            "description_uz": "Yurtada nonushta. Nukusga qaytish (450 km, 8 soat). Yo'lda: Qurgancha-Qal'a karvonsaroyi (XIII asr), Sudochye ko'li, Urga qishlog'i. Kunqirad shaharchasida tushlik. Mizdaxkon nekropoli ('Apokalipsis soatlari', Nazlumxon maqbarasi). Aeroportga transfer va Toshkentga reys.",
            "description_ru": "Завтрак в юрте. Возвращение в Нукус (450 км, 8 часов). По пути: караван-сарай Курганча-Кала (XIII в.), озеро Судочье, посёлок Урга. Обед в Кунграде. Некрополь Миздахкан («Часы Апокалипсиса», мавзолей Назлум-хана). Трансфер в аэропорт и вылет в Ташкент.",
            "description_en": "Breakfast in yurt. Return to Nukus (450 km, 8 hours). En route: Kurgancha-Kala caravanserai (13th c.), Sudochie lake, Urga village. Lunch in Kungrad. Mizdakhan necropolis ('Apocalypse Clock', Nazlum-khan mausoleum). Airport transfer and flight to Tashkent.",
            "description_ko": "유르트에서 조식. 누쿠스로 돌아옴 (450km, 8시간). 도중에: 쿠르간차-칼라 카라반세라이 (13세기), 수도치에 호수, 우르가 마을. 쿤그라드에서 중식. 미즈다칸 네크로폴리스 ('종말의 시계', 나즐룸-칸 영묘). 공항 트랜스퍼와 타슈켄트행 비행.",
        },
        {
            "day": 3,
            "title_uz": "Toshkent → Keyingi nuqtaga",
            "title_ru": "Ташкент → Следующий пункт",
            "title_en": "Tashkent → Next destination",
            "title_ko": "타슈켄트 → 다음 목적지",
            "description_uz": "Mehmonxonada nonushta. Aeroportga transfer. Dasturning yakuni.",
            "description_ru": "Завтрак в отеле. Трансфер в аэропорт. Окончание программы.",
            "description_en": "Hotel breakfast. Airport transfer. End of program.",
            "description_ko": "호텔 조식. 공항 트랜스퍼. 프로그램 종료.",
        },
    ],
}


class Command(BaseCommand):
    help = "Tour itinerary (kunma-kun dastur)larni DBga yozadi"

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            Tour = apps.get_model('tours', 'Tour')
        except LookupError:
            self.stderr.write("Tour modeli topilmadi")
            return

        # Itinerary model nomini topish
        ItineraryDay = None
        for model_name in ['ItineraryDay', 'TourDay', 'TourItinerary', 'Day']:
            try:
                ItineraryDay = apps.get_model('tours', model_name)
                self.stdout.write(f"✓ {model_name} modeli topildi")
                break
            except LookupError:
                continue

        if not ItineraryDay:
            self.stdout.write(self.style.WARNING(
                "Itinerary modeli topilmadi (ItineraryDay/TourDay/TourItinerary).\n"
                "Iltimos, models.py da quyidagi modelni qo'shing:\n\n"
                "class ItineraryDay(models.Model):\n"
                "    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary')\n"
                "    day = models.PositiveIntegerField()\n"
                "    title = models.CharField(max_length=200)\n"
                "    description = models.TextField()\n"
                "    class Meta:\n"
                "        ordering = ['day']"
            ))
            return

        for tour_slug, days in ITINERARIES.items():
            try:
                tour = Tour.objects.get(slug=tour_slug)
            except Tour.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ✗ Tour topilmadi: {tour_slug}"))
                continue

            ItineraryDay.objects.filter(tour=tour).delete()

            for d in days:
                defaults = {}
                # Translation field'larni topish
                model_fields = {f.name for f in ItineraryDay._meta.get_fields()}
                for key, val in d.items():
                    if key == 'day':
                        defaults['day'] = val
                    elif key in model_fields:
                        defaults[key] = val
                # title/description fallback
                if 'title' in model_fields and 'title' not in defaults:
                    defaults['title'] = d.get('title_uz', '')
                if 'description' in model_fields and 'description' not in defaults:
                    defaults['description'] = d.get('description_uz', '')

                ItineraryDay.objects.create(tour=tour, **defaults)

            self.stdout.write(f"  ✓ {tour_slug}: {len(days)} kun")

        self.stdout.write(self.style.SUCCESS("\n✅ Itinerary'lar DBga yozildi!"))