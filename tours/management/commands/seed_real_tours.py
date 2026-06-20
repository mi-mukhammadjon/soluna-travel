"""
Django management command to seed real Uzbekistan tours.

Joylash:
  tours/management/__init__.py        (bo'sh fayl)
  tours/management/commands/__init__.py (bo'sh fayl)
  tours/management/commands/seed_real_tours.py  ← BU FAYL

Ishlatish:
  docker compose exec web python manage.py seed_real_tours
  
  Yoki yangidan:
  docker compose exec web python manage.py seed_real_tours --clear

  Faqat regionlarni qayta seed qilish:
  docker compose exec web python manage.py seed_real_tours --regions-only
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.apps import apps


# ════════════════════════════════════════════════════════════════════
# REGIONS DATA — Uzbekistan main destinations (UZ/RU/EN/KO)
# ════════════════════════════════════════════════════════════════════
REGIONS_DATA = [
    {
        "slug": "tashkent",
        "name_uz": "Toshkent",
        "name_ru": "Ташкент",
        "name_en": "Tashkent",
        "name_ko": "타슈켄트",
        "description_uz": "O'zbekiston poytaxti, zamonaviy va qadimiy uyg'unligi. Xast-Imom majmuasi, Chorsu bozori, Mustaqillik maydoni va Amir Temur xiyoboni.",
        "description_ru": "Столица Узбекистана, гармония современности и древности. Комплекс Хаст-Имам, базар Чорсу, площадь Независимости и сквер Амира Темура.",
        "description_en": "Capital of Uzbekistan, where ancient meets modern. Visit Khast-Imam complex, Chorsu bazaar, Independence Square, and Amir Temur square.",
        "description_ko": "우즈베키스탄의 수도, 고대와 현대의 조화. 하스트이맘 단지, 초르수 시장, 독립광장, 아미르 티무르 광장을 방문하세요.",
        "country": "Uzbekistan",
        "latitude": 41.2995,
        "longitude": 69.2401,
    },
    {
        "slug": "samarkand",
        "name_uz": "Samarqand",
        "name_ru": "Самарканд",
        "name_en": "Samarkand",
        "name_ko": "사마르칸트",
        "description_uz": "Buyuk Ipak yo'lining marvaridi, UNESCO ro'yxatidagi shahar. Registon maydoni, Bibi-Xonim masjidi, Shohi-Zinda nekropoli va Go'ri Amir maqbarasi.",
        "description_ru": "Жемчужина Великого шёлкового пути, город из списка ЮНЕСКО. Площадь Регистан, мечеть Биби-Ханым, некрополь Шахи-Зинда и мавзолей Гур-Эмир.",
        "description_en": "Pearl of the Great Silk Road, UNESCO World Heritage city. Registan Square, Bibi-Khanym Mosque, Shah-i-Zinda necropolis, and Gur-e-Amir mausoleum.",
        "description_ko": "위대한 실크로드의 진주, 유네스코 세계유산 도시. 레기스탄 광장, 비비하늠 모스크, 샤히진다 네크로폴리스, 구르 에미르 영묘.",
        "country": "Uzbekistan",
        "latitude": 39.6542,
        "longitude": 66.9597,
    },
    {
        "slug": "bukhara",
        "name_uz": "Buxoro",
        "name_ru": "Бухара",
        "name_en": "Bukhara",
        "name_ko": "부하라",
        "description_uz": "2500 yillik tarixga ega muqaddas shahar, butun shahar ochiq osmon ostidagi muzey. Po'i-Kalon majmuasi, Ark qal'asi, Labi-Hovuz va savdo gumbazlari.",
        "description_ru": "Священный город с 2500-летней историей, целый город — музей под открытым небом. Комплекс Пои-Калян, крепость Арк, Ляби-Хауз и торговые купола.",
        "description_en": "Sacred city with 2,500 years of history — an open-air museum. Poi-Kalyan complex, Ark fortress, Lyab-i-Hauz, and trading domes.",
        "description_ko": "2500년 역사의 신성한 도시, 야외 박물관 전체. 포이칼란 단지, 아르크 요새, 라비하우즈, 무역 돔.",
        "country": "Uzbekistan",
        "latitude": 39.7681,
        "longitude": 64.4556,
    },
    {
        "slug": "khiva",
        "name_uz": "Xiva",
        "name_ru": "Хива",
        "name_en": "Khiva",
        "name_ko": "히바",
        "description_uz": "Ichan-Qal'a — devor bilan o'ralgan qadimiy shahar, UNESCO yodgorligi. Kalta-Minor minorasi, Muhammad Aminxon madrasasi, Toshhovli saroyi.",
        "description_ru": "Ичан-Кала — древний город за стенами, объект ЮНЕСКО. Минарет Кальта-Минор, медресе Мухаммад Амин-хана, дворец Таш-Ховли.",
        "description_en": "Ichan-Kala — ancient walled city, UNESCO World Heritage. Kalta-Minor minaret, Mohammed Amin Khan madrasah, Tash-Hauli palace.",
        "description_ko": "이찬칼라 — 성벽으로 둘러싸인 고대 도시, 유네스코 세계유산. 칼타미노르 미나레트, 무함마드 아민 칸 마드라사, 타시하울리 궁전.",
        "country": "Uzbekistan",
        "latitude": 41.3783,
        "longitude": 60.3617,
    },
    {
        "slug": "nukus-aral",
        "name_uz": "Nukus va Orol",
        "name_ru": "Нукус и Арал",
        "name_en": "Nukus & Aral Sea",
        "name_ko": "누쿠스 & 아랄해",
        "description_uz": "Qoraqalpog'iston poytaxti va Orol dengizi sarguzashti. Mo'ynoq kemalar qabristoni, Ustyurt platosi, Mizdaxkon nekropoli.",
        "description_ru": "Столица Каракалпакстана и приключение к Аральскому морю. Кладбище кораблей в Муйнаке, плато Устюрт, некрополь Миздахкан.",
        "description_en": "Capital of Karakalpakstan and adventure to the Aral Sea. Moynaq ship cemetery, Ustyurt plateau, Mizdakhan necropolis.",
        "description_ko": "카라칼팍스탄의 수도와 아랄해 모험. 모이낙 선박 묘지, 우스튜르트 고원, 미즈다칸 네크로폴리스.",
        "country": "Uzbekistan",
        "latitude": 42.4531,
        "longitude": 59.6103,
    },
    {
        "slug": "urgench",
        "name_uz": "Urganch",
        "name_ru": "Ургенч",
        "name_en": "Urgench",
        "name_ko": "우르겐치",
        "description_uz": "Xorazm viloyati markazi, Xivaga eshik. Aviakompaniyalar boyog'i, qadimiy Xorazm madaniyatining vorisi.",
        "description_ru": "Центр Хорезмской области, ворота в Хиву. Авиационный узел, наследник древней хорезмской культуры.",
        "description_en": "Capital of Khorezm region, gateway to Khiva. Air travel hub, heir to ancient Khorezm culture.",
        "description_ko": "호레즘 지방의 수도, 히바로 가는 관문. 항공 허브, 고대 호레즘 문화의 계승자.",
        "country": "Uzbekistan",
        "latitude": 41.5500,
        "longitude": 60.6333,
    },
]


# ════════════════════════════════════════════════════════════════════
# CATEGORIES
# ════════════════════════════════════════════════════════════════════
CATEGORIES_DATA = [
    {"slug": "classic", "name_uz": "Klassik turlar", "name_ru": "Классические туры",
     "name_en": "Classic Tours", "name_ko": "클래식 투어"},
    {"slug": "silk-road", "name_uz": "Ipak yo'li", "name_ru": "Шёлковый путь",
     "name_en": "Silk Road", "name_ko": "실크로드"},
    {"slug": "adventure", "name_uz": "Sarguzasht", "name_ru": "Приключения",
     "name_en": "Adventure", "name_ko": "어드벤처"},
    {"slug": "cultural", "name_uz": "Madaniy", "name_ru": "Культурные",
     "name_en": "Cultural", "name_ko": "문화"},
    {"slug": "desert", "name_uz": "Cho'l", "name_ru": "Пустыня",
     "name_en": "Desert", "name_ko": "사막"},
]


# ════════════════════════════════════════════════════════════════════
# TOURS DATA — based on real .docx files
# ════════════════════════════════════════════════════════════════════
TOURS_DATA = [

    # ── Tour 1: Toshkent-Samarqand-Buxoro (8 kun) ───────────────────
    {
        "slug": "uzbekistan-tashkent-samarkand-bukhara-8d",
        "name_uz": "O'zbekiston bo'ylab tur: Toshkent – Samarqand – Buxoro",
        "name_ru": "Тур по Узбекистану: Ташкент – Самарканд – Бухара",
        "name_en": "Uzbekistan Tour: Tashkent – Samarkand – Bukhara",
        "name_ko": "우즈베키스탄 투어: 타슈켄트 – 사마르칸트 – 부하라",

        "short_description_uz": "8 kun / 7 tun. Toshkent, Samarqand va Buxoroni o'z ichiga olgan klassik tur. Afrosiyob tezyurar poyezdida sayohat.",
        "short_description_ru": "8 дней / 7 ночей. Классический тур с посещением Ташкента, Самарканда и Бухары. Поездки на скоростном поезде «Афросиаб».",
        "short_description_en": "8 days / 7 nights. Classic tour covering Tashkent, Samarkand, and Bukhara. Travel by Afrosiyob high-speed train.",
        "short_description_ko": "8일 / 7박. 타슈켄트, 사마르칸트, 부하라를 포함하는 클래식 투어. 아프로시얍 고속열차 이동.",

        "description_uz": """8 kunlik klassik O'zbekiston turi.

Marshrut: Toshkent – Samarqand – Buxoro – Toshkent
Davomiyligi: 8 kun / 7 tun

Tashriflar:
• Toshkent: Xast-Imom maydoni, Baroqxon madrasasi, Tilla-Shayx masjidi, Chorsu bozori, Mustaqillik maydoni, Amir Temur xiyoboni
• Samarqand: Registon maydoni, Go'ri Amir maqbarasi, Bibi-Xonim masjidi, Siyob bozori, Shohi-Zinda nekropoli, Ulug'bek rasadxonasi
• Buxoro: Labi-Hovuz, Ko'kaldosh madrasasi, savdo gumbazlari, Ark qal'asi, Bolo-Hovuz masjidi, Po'i-Kalon majmuasi, Somoniylar maqbarasi""",

        "description_ru": """8-дневный классический тур по Узбекистану.

Маршрут: Ташкент – Самарканд – Бухара – Ташкент
Продолжительность: 8 дней / 7 ночей

Посещения:
• Ташкент: площадь Хаст-Имам, медресе Баракхан, мечеть Тилля-Шейх, базар Чорсу, площадь Независимости, сквер Амира Темура
• Самарканд: площадь Регистан, мавзолей Гур-Эмир, мечеть Биби-Ханым, Сиабский базар, некрополь Шахи-Зинда, обсерватория Улугбека
• Бухара: Ляби-Хауз, медресе Кукельдаш, торговые купола, крепость Арк, мечеть Боло-Хауз, комплекс Пои-Калян, мавзолей Саманидов""",

        "description_en": """8-day classic Uzbekistan tour.

Route: Tashkent – Samarkand – Bukhara – Tashkent
Duration: 8 days / 7 nights

Highlights:
• Tashkent: Khast-Imam square, Barak-Khan madrasah, Tilla-Sheikh mosque, Chorsu bazaar, Independence square, Amir Temur square
• Samarkand: Registan Square, Gur-e-Amir mausoleum, Bibi-Khanym mosque, Siab bazaar, Shah-i-Zinda necropolis, Ulugh Beg observatory
• Bukhara: Lyab-i-Hauz, Kukeldash madrasah, trading domes, Ark fortress, Bolo-Hauz mosque, Poi-Kalyan complex, Samanid mausoleum""",

        "description_ko": """8일 클래식 우즈베키스탄 투어.

루트: 타슈켄트 – 사마르칸트 – 부하라 – 타슈켄트
기간: 8일 / 7박

하이라이트:
• 타슈켄트: 하스트이맘 광장, 바라크칸 마드라사, 틸라셰이크 모스크, 초르수 시장, 독립광장, 아미르 티무르 광장
• 사마르칸트: 레기스탄 광장, 구르 에미르 영묘, 비비하늠 모스크, 시압 시장, 샤히진다 네크로폴리스, 울루그벡 천문대
• 부하라: 라비하우즈, 쿠켈다시 마드라사, 무역 돔, 아르크 요새, 볼로하우즈 모스크, 포이칼란 단지, 사마니드 영묘""",

        "price": Decimal("1190"),
        "single_supplement": Decimal("200"),
        "duration_days": 8,
        "duration_nights": 7,
        "min_people": 2,
        "max_people": 16,
        "rating": Decimal("4.96"),
        "review_count": 672,
        "tour_type": "Cultural",
        "is_featured": True,
        "is_top_rated": True,
        "category_slug": "classic",
        "region_slug": "samarkand",
        "image_url": "https://images.unsplash.com/photo-1591708594806-1eaa84a8e4f8?w=1200",

        "included_uz": [
            "Tanlangan toifadagi mehmonxonalarda joylashish",
            "Nonushtalar",
            "Aeroport – mehmonxona – aeroport transferi",
            "Toshkent – Samarqand – Buxoro – Toshkent temir yo'l chiptalari",
            "Rus tilida gid bilan ekskursiyalar",
            "Ko'rsatilgan ob'ektlarga kirish chiptalari",
        ],
        "included_ru": [
            "Размещение в отелях выбранной категории",
            "Завтраки",
            "Трансферы аэропорт – отель – аэропорт",
            "Ж/д билеты Ташкент – Самарканд – Бухара – Ташкент",
            "Экскурсии с русскоговорящим гидом",
            "Входные билеты на указанные объекты",
        ],
        "included_en": [
            "Hotel accommodation (selected category)",
            "Daily breakfast",
            "Airport – hotel – airport transfers",
            "Train tickets Tashkent – Samarkand – Bukhara – Tashkent",
            "Sightseeing with English-speaking guide",
            "Entrance fees as per program",
        ],
        "included_ko": [
            "선택한 등급의 호텔 숙박",
            "조식 포함",
            "공항 – 호텔 – 공항 트랜스퍼",
            "기차표 타슈켄트 – 사마르칸트 – 부하라 – 타슈켄트",
            "한국어/영어 가이드 관광",
            "프로그램에 명시된 입장료",
        ],
        "excluded_uz": ["Xalqaro aviachiptalar", "Sug'urta", "Shaxsiy xarajatlar"],
        "excluded_ru": ["Международные авиабилеты", "Страховка", "Личные расходы"],
        "excluded_en": ["International flights", "Travel insurance", "Personal expenses"],
        "excluded_ko": ["국제 항공권", "여행자 보험", "개인 비용"],
    },

    # ── Tour 2: ARAL (3 kun) ────────────────────────────────────────
    {
        "slug": "aral-sea-3d-adventure",
        "name_uz": "Orol dengizi sarguzashti — 3 kun",
        "name_ru": "Аральское море — 3 дня",
        "name_en": "Aral Sea Adventure — 3 days",
        "name_ko": "아랄해 어드벤처 — 3일",

        "short_description_uz": "3 kun / 2 tun. Mo'ynoq kemalar qabristoni, Ustyurt platosi va yurtada tunash bilan jip-tur 4×4.",
        "short_description_ru": "3 дня / 2 ночи. Кладбище кораблей в Муйнаке, плато Устюрт и ночёвка в юрте — джип-тур 4×4.",
        "short_description_en": "3 days / 2 nights. Moynaq ship cemetery, Ustyurt plateau and yurt camp overnight — 4×4 jeep tour.",
        "short_description_ko": "3일 / 2박. 모이낙 선박 묘지, 우스튜르트 고원, 유르트 캠프 숙박 — 4×4 지프 투어.",

        "description_uz": """Ekologik halokat zonasiga unutilmas sarguzasht.

Marshrut: Toshkent – Nukus – Mo'ynoq – Ustyurt platosi – Orol dengizi – Nukus – Toshkent
Davomiyligi: 3 kun / 2 tun
Mavsum: 20 aprel – 20 oktyabr

1-kun: Nukusga uchish, Mo'ynoqqa borish (kemalar qabristoni va muzey), Ustyurt platosi kanyoni, yurtada tunash.
2-kun: Sudochye ko'li, Mizdaxkon nekropoli, Nukusga qaytish va Toshkentga uchish.
3-kun: Nonushta, aeroportga transfer.

DIQQAT: Yo'l mobil aloqasi va mehmonxonasiz hududdan o'tadi.""",

        "description_ru": """Незабываемое приключение в зону экологической катастрофы.

Маршрут: Ташкент – Нукус – Муйнак – Плато Устюрт – Аральское море – Нукус – Ташкент
Продолжительность: 3 дня / 2 ночи
Сезон: 20 апреля – 20 октября

День 1: Перелёт в Нукус, поездка в Муйнак (кладбище кораблей и музей), каньон плато Устюрт, ночёвка в юрте.
День 2: Озеро Судочье, некрополь Миздахкан, возвращение в Нукус и вылет в Ташкент.
День 3: Завтрак, трансфер в аэропорт.

ВНИМАНИЕ: Маршрут проходит по местности без мобильной связи и гостиниц.""",

        "description_en": """Unforgettable adventure to the zone of ecological catastrophe.

Route: Tashkent – Nukus – Moynaq – Ustyurt Plateau – Aral Sea – Nukus – Tashkent
Duration: 3 days / 2 nights
Season: April 20 – October 20

Day 1: Flight to Nukus, drive to Moynaq (ship cemetery and museum), Ustyurt plateau canyon, overnight in yurt camp.
Day 2: Sudochie lake, Mizdakhan necropolis, return to Nukus and flight to Tashkent.
Day 3: Breakfast, airport transfer.

NOTE: Route passes through areas without mobile coverage or hotels.""",

        "description_ko": """생태 재앙 지역으로의 잊을 수 없는 모험.

루트: 타슈켄트 – 누쿠스 – 모이낙 – 우스튜르트 고원 – 아랄해 – 누쿠스 – 타슈켄트
기간: 3일 / 2박
시즌: 4월 20일 – 10월 20일

1일차: 누쿠스로 비행, 모이낙으로 이동 (선박 묘지와 박물관), 우스튜르트 고원 협곡, 유르트 캠프 숙박.
2일차: 수도치에 호수, 미즈다칸 네크로폴리스, 누쿠스로 돌아와 타슈켄트행 비행.
3일차: 조식, 공항 트랜스퍼.

주의: 루트는 모바일 통신과 호텔이 없는 지역을 통과합니다.""",

        "price": Decimal("600"),
        "single_supplement": Decimal("50"),
        "duration_days": 3,
        "duration_nights": 2,
        "min_people": 2,
        "max_people": 8,
        "rating": Decimal("4.85"),
        "review_count": 124,
        "tour_type": "Adventure",
        "is_featured": True,
        "is_best_sale": True,
        "category_slug": "adventure",
        "region_slug": "nukus-aral",
        "image_url": "https://images.unsplash.com/photo-1565008447742-97f6f38c985c?w=1200",

        "included_uz": [
            "Joylashish: mehmonxonada 1 tun (DBL/TWN) + yurtada 1 tun",
            "Ovqatlar: 2 nonushta, 2 tushlik, 1 kechki ovqat",
            "Ovqat vaqtida choy va suv",
            "Aviachiptalar Toshkent – Nukus – Toshkent (econom)",
            "Muzey va yodgorliklarga kirish chiptalari",
            "Orol dengiziga 4×4 jip-tur",
            "Toshkentdagi transferlar",
            "Orol mintaqasida ingliz tilida gid",
        ],
        "included_ru": [
            "Проживание: 1 ночь в отеле (DBL/TWN) + 1 ночь в юрте",
            "Питание: 2 завтрака, 2 обеда, 1 ужин",
            "Чай и вода во время приёмов пищи",
            "Авиабилеты Ташкент – Нукус – Ташкент (эконом)",
            "Входные билеты в музеи и памятники",
            "Тур к Аральскому морю на джипах 4×4",
            "Трансферы в Ташкенте",
            "Англоговорящий гид в регионе Арала",
        ],
        "included_en": [
            "Accommodation: 1 night in hotel (DBL/TWN) + 1 night in yurt",
            "Meals: 2 breakfasts, 2 lunches, 1 dinner",
            "Tea and water during meals",
            "Flights Tashkent – Nukus – Tashkent (economy)",
            "Museum and monument entrance fees",
            "4×4 jeep tour to the Aral Sea",
            "Transfers in Tashkent",
            "English-speaking guide in the Aral region",
        ],
        "included_ko": [
            "숙박: 호텔 1박 (DBL/TWN) + 유르트 1박",
            "식사: 조식 2회, 중식 2회, 석식 1회",
            "식사 중 차와 물",
            "타슈켄트 – 누쿠스 – 타슈켄트 항공편 (이코노미)",
            "박물관 및 기념물 입장료",
            "아랄해로 4×4 지프 투어",
            "타슈켄트 내 트랜스퍼",
            "아랄 지역 영어 가이드",
        ],
        "excluded_uz": ["Erta joylashish/kech chiqish", "Ichimliklar", "Foto/video to'lovi", "Choychaqa"],
        "excluded_ru": ["Раннее заселение/поздний выезд", "Напитки", "Плата за фото/видео", "Чаевые"],
        "excluded_en": ["Early check-in/late check-out", "Drinks", "Photo/video fees", "Tips"],
        "excluded_ko": ["얼리 체크인/레이트 체크아웃", "음료", "사진/비디오 촬영비", "팁"],
    },

    # ── Tour 3: Classic Uzbekistan TAS-TAS (8 kun) ──────────────────
    {
        "slug": "classic-uzbekistan-tas-tas-8d",
        "name_uz": "Klassik O'zbekiston (Toshkent – Xiva – Buxoro – Samarqand)",
        "name_ru": "Классический Узбекистан (Ташкент – Хива – Бухара – Самарканд)",
        "name_en": "Classic Uzbekistan (Tashkent – Khiva – Bukhara – Samarkand)",
        "name_ko": "클래식 우즈베키스탄 (타슈켄트 – 히바 – 부하라 – 사마르칸트)",

        "short_description_uz": "8 kun / 7 tun guruh turi. To'rtta UNESCO shahriga sayohat. Har shanba jo'nash.",
        "short_description_ru": "8 дней / 7 ночей групповой тур. Посещение четырёх городов ЮНЕСКО. Заезды каждую субботу.",
        "short_description_en": "8 days / 7 nights group tour visiting four UNESCO cities. Saturday departures.",
        "short_description_ko": "8일 / 7박 그룹 투어, 4개의 유네스코 도시 방문. 토요일 출발.",

        "description_uz": """O'zbekistonning eng to'liq klassik tur.

Marshrut: Toshkent – Urganch – Xiva – Buxoro – Samarqand – Toshkent
Jo'nashlar: Har shanba
Eng kam: 2 ishtirokchi

Asosiy ko'rinishlar:
• Toshkent: Xast-Imom, Chorsu, Mustaqillik
• Xiva: Ichan-Qal'a (UNESCO), Kalta-Minor, Toshhovli
• Buxoro: Somoniylar maqbarasi, Po'i-Kalon, Ark
• Samarqand: Registon, Go'ri Amir, Shohi-Zinda, Bibi-Xonim
• Samarqanddan Toshkentga tezyurar poyezd""",

        "description_ru": """Самый полный классический тур по Узбекистану.

Маршрут: Ташкент – Ургенч – Хива – Бухара – Самарканд – Ташкент
Заезды: каждую субботу
Минимум: 2 участника

Главные достопримечательности:
• Ташкент: Хаст-Имам, Чорсу, Независимость
• Хива: Ичан-Кала (ЮНЕСКО), Кальта-Минор, Таш-Ховли
• Бухара: мавзолей Саманидов, Пои-Калян, Арк
• Самарканд: Регистан, Гур-Эмир, Шахи-Зинда, Биби-Ханым
• Скоростной поезд Самарканд – Ташкент""",

        "description_en": """The most comprehensive classic tour of Uzbekistan.

Route: Tashkent – Urgench – Khiva – Bukhara – Samarkand – Tashkent
Departures: Every Saturday
Minimum: 2 participants

Main highlights:
• Tashkent: Khast-Imam, Chorsu, Independence
• Khiva: Ichan-Kala (UNESCO), Kalta-Minor, Tash-Hauli
• Bukhara: Samanid mausoleum, Poi-Kalyan, Ark
• Samarkand: Registan, Gur-e-Amir, Shah-i-Zinda, Bibi-Khanym
• High-speed train Samarkand – Tashkent""",

        "description_ko": """가장 종합적인 클래식 우즈베키스탄 투어.

루트: 타슈켄트 – 우르겐치 – 히바 – 부하라 – 사마르칸트 – 타슈켄트
출발: 매주 토요일
최소: 2명

주요 명소:
• 타슈켄트: 하스트이맘, 초르수, 독립광장
• 히바: 이찬칼라 (유네스코), 칼타미노르, 타시하울리
• 부하라: 사마니드 영묘, 포이칼란, 아르크
• 사마르칸트: 레기스탄, 구르 에미르, 샤히진다, 비비하늠
• 사마르칸트 – 타슈켄트 고속열차""",

        "price": Decimal("1190"),
        "single_supplement": Decimal("200"),
        "duration_days": 8,
        "duration_nights": 7,
        "min_people": 2,
        "max_people": 16,
        "rating": Decimal("4.92"),
        "review_count": 489,
        "tour_type": "Cultural",
        "is_featured": True,
        "is_top_rated": True,
        "category_slug": "classic",
        "region_slug": "samarkand",
        "image_url": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=1200",

        "included_uz": [
            "Ikki kishilik xonada 7 tun joylashish",
            "Erta keldi joylashish",
            "7 nonushta va 6 tushlik",
            "Tushlik vaqtida choy va suv",
            "Konditsionerli transport va transferlar",
            "Dasturdagi kirish chiptalari",
            "Ichki parvoz Toshkent – Urganch",
            "Samarqand – Toshkent poyezd chiptasi",
            "Gid xizmati",
        ],
        "included_ru": [
            "Проживание 7 ночей в двухместном номере",
            "Раннее заселение в день прибытия",
            "7 завтраков и 6 обедов",
            "Чай и вода во время обедов",
            "Все трансферы и транспорт с кондиционером",
            "Входные билеты по программе",
            "Внутренний перелёт Ташкент – Ургенч",
            "Билет на поезд Самарканд – Ташкент",
            "Услуги гида",
        ],
        "included_en": [
            "7 nights accommodation in double room",
            "Early check-in on arrival day",
            "7 breakfasts and 6 lunches",
            "Tea and water during lunches",
            "All transfers and AC transport",
            "Entrance fees per program",
            "Domestic flight Tashkent – Urgench",
            "Train ticket Samarkand – Tashkent",
            "Guide services",
        ],
        "included_ko": [
            "더블룸 7박 숙박",
            "도착일 얼리 체크인",
            "조식 7회, 중식 6회",
            "중식 시 차와 물",
            "에어컨 차량 및 모든 트랜스퍼",
            "프로그램 입장료",
            "국내선 타슈켄트 – 우르겐치",
            "사마르칸트 – 타슈켄트 기차표",
            "가이드 서비스",
        ],
        "excluded_uz": ["Xalqaro aviachiptalar", "Vizalar", "Foto/video to'lovlari", "Choychaqa (45 EUR)"],
        "excluded_ru": ["Международные авиабилеты", "Визы", "Фото/видео сборы", "Чаевые (45 EUR)"],
        "excluded_en": ["International flights", "Visas", "Photo/video fees", "Tips (45 EUR)"],
        "excluded_ko": ["국제 항공권", "비자", "사진/비디오 촬영비", "팁 (45 EUR)"],
    },

    # ── Tour 4: Silk Road (8 kun) ───────────────────────────────────
    {
        "slug": "silk-road-uzbekistan-8d",
        "name_uz": "Ipak yo'li: O'zbekiston bo'ylab guruh turi 2026",
        "name_ru": "Шёлковый путь: Групповой тур по Узбекистану 2026",
        "name_en": "Silk Road: Uzbekistan Group Tour 2026",
        "name_ko": "실크로드: 우즈베키스탄 그룹 투어 2026",

        "short_description_uz": "8 kunlik tarixiy Ipak yo'li sayohat. Har dushanba jo'nash. Eng yaxshi narx — 900 USD.",
        "short_description_ru": "8-дневное путешествие по историческому Шёлковому пути. Заезды каждый понедельник. Лучшая цена — 900 USD.",
        "short_description_en": "8-day historic Silk Road journey. Monday departures. Best price — $900.",
        "short_description_ko": "8일 역사적인 실크로드 여행. 월요일 출발. 최고 가격 — $900.",

        "description_uz": """O'zbekiston bo'ylab Buyuk Ipak yo'lining toshlari ustidan o'tuvchi sayohat.

Marshrut: Toshkent – Samarqand – Buxoro – Xiva – Urganch
Jo'nashlar: Har dushanba
Davomiyligi: 8 kun

Bu tur ispanzabon gid bilan ham mavjud. Qizilqum cho'li orqali Xivaga o'tish kabi maxsus marshrut.""",

        "description_ru": """Путешествие по камням Великого шёлкового пути в Узбекистане.

Маршрут: Ташкент – Самарканд – Бухара – Хива – Ургенч
Заезды: каждый понедельник
Продолжительность: 8 дней

Тур доступен и с испаноговорящим гидом. Особенный маршрут — переход через пустыню Кызылкум в Хиву.""",

        "description_en": """Journey through the stones of the Great Silk Road in Uzbekistan.

Route: Tashkent – Samarkand – Bukhara – Khiva – Urgench
Departures: Every Monday
Duration: 8 days

Available with Spanish-speaking guide. Unique route — crossing the Kyzylkum desert to Khiva.""",

        "description_ko": """우즈베키스탄의 위대한 실크로드의 돌들을 따라가는 여행.

루트: 타슈켄트 – 사마르칸트 – 부하라 – 히바 – 우르겐치
출발: 매주 월요일
기간: 8일

스페인어 가이드도 가능. 키질쿰 사막을 건너 히바로 가는 특별한 루트.""",

        "price": Decimal("900"),
        "single_supplement": Decimal("180"),
        "duration_days": 8,
        "duration_nights": 7,
        "min_people": 2,
        "max_people": 20,
        "rating": Decimal("4.88"),
        "review_count": 312,
        "tour_type": "Cultural",
        "is_featured": True,
        "is_best_sale": True,
        "category_slug": "silk-road",
        "region_slug": "bukhara",
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1200",
        "discount_percent": 15,

        "included_uz": [
            "Ikki kishilik xonada 6 tun",
            "Nonushtalar",
            "Konditsionerli transport va transferlar",
            "Dasturdagi kirish chiptalari",
            "Ispanzabon/Inglizzabon gid",
            "Turistik xarita va sovg'alar",
        ],
        "included_ru": [
            "Проживание 6 ночей в двухместном номере",
            "Завтраки",
            "Все трансферы и транспорт с кондиционером",
            "Входные билеты по программе",
            "Услуги испаноговорящего/англоговорящего гида",
            "Туристическая карта и сувениры",
        ],
        "included_en": [
            "6 nights in double room",
            "Breakfasts",
            "All AC transfers and transport",
            "Entrance fees per program",
            "Spanish/English-speaking guide",
            "Tourist map and souvenirs",
        ],
        "included_ko": [
            "더블룸 6박",
            "조식",
            "에어컨 트랜스퍼와 차량",
            "프로그램별 입장료",
            "스페인어/영어 가이드",
            "관광 지도와 기념품",
        ],
        "excluded_uz": ["Xalqaro aviachiptalar", "Viza", "Choychaqa (45 EUR)", "Toshkent-Samarqand poyezd (30 USD)", "Tushlik va kechki ovqat"],
        "excluded_ru": ["Международные авиабилеты", "Виза", "Чаевые (45 EUR)", "Поезд Ташкент-Самарканд (30 USD)", "Обеды и ужины"],
        "excluded_en": ["International flights", "Visa", "Tips (45 EUR)", "Tashkent-Samarkand train ($30)", "Lunches and dinners"],
        "excluded_ko": ["국제 항공권", "비자", "팁 (45 EUR)", "타슈켄트-사마르칸트 기차 ($30)", "중식과 석식"],
    },

    # ── Tour 5: Premium Spanish-speaking (8 kun) ────────────────────
    {
        "slug": "uzbekistan-premium-spanish-8d",
        "name_uz": "O'zbekiston Premium: Ispanzabon gid bilan",
        "name_ru": "Узбекистан Премиум: с испаноговорящим гидом",
        "name_en": "Uzbekistan Premium: with Spanish-speaking guide",
        "name_ko": "우즈베키스탄 프리미엄: 스페인어 가이드 동행",

        "short_description_uz": "8 kun premium tur. Madrid – Toshkent uchish. Uzbekistan Airways bilan. Har dushanba jo'nash.",
        "short_description_ru": "8 дней премиум-тур. Перелёт Мадрид – Ташкент. Uzbekistan Airways. Заезды каждый понедельник.",
        "short_description_en": "8-day premium tour. Madrid – Tashkent flight. Uzbekistan Airways. Monday departures.",
        "short_description_ko": "8일 프리미엄 투어. 마드리드 – 타슈켄트 항공. 우즈베키스탄 항공. 월요일 출발.",

        "description_uz": """Ispaniyalik mehmonlar uchun maxsus premium tur.

Marshrut: Madrid – Toshkent – Samarqand – Buxoro – Xiva – Urganch – Madrid
Davomiyligi: 8 kun
Aviakompaniya: Uzbekistan Airways (HY)

Boshlanish: Dushanba kuni Madriddan 18:35 da uchish, seshanba 04:40 da Toshkentda qo'nish.""",

        "description_ru": """Премиум-тур специально для гостей из Испании.

Маршрут: Мадрид – Ташкент – Самарканд – Бухара – Хива – Ургенч – Мадрид
Продолжительность: 8 дней
Авиакомпания: Uzbekistan Airways (HY)

Начало: вылет из Мадрида в понедельник в 18:35, прибытие в Ташкент во вторник в 04:40.""",

        "description_en": """Premium tour specially designed for Spanish guests.

Route: Madrid – Tashkent – Samarkand – Bukhara – Khiva – Urgench – Madrid
Duration: 8 days
Airline: Uzbekistan Airways (HY)

Start: Departure from Madrid on Monday at 18:35, arrival in Tashkent on Tuesday at 04:40.""",

        "description_ko": """스페인 손님을 위해 특별히 설계된 프리미엄 투어.

루트: 마드리드 – 타슈켄트 – 사마르칸트 – 부하라 – 히바 – 우르겐치 – 마드리드
기간: 8일
항공사: 우즈베키스탄 항공 (HY)

시작: 월요일 마드리드 18:35 출발, 화요일 타슈켄트 04:40 도착.""",

        "price": Decimal("1450"),
        "single_supplement": Decimal("280"),
        "duration_days": 8,
        "duration_nights": 7,
        "min_people": 2,
        "max_people": 20,
        "rating": Decimal("4.94"),
        "review_count": 218,
        "tour_type": "Premium",
        "is_featured": True,
        "is_top_rated": True,
        "category_slug": "silk-road",
        "region_slug": "samarkand",
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1200",

        "included_uz": [
            "Madrid-Toshkent xalqaro reys (Uzbekistan Airways)",
            "7 tun 4* mehmonxonalarda",
            "Barcha nonushtalar",
            "Konditsionerli transport",
            "Afrosiyob tezyurar poyezd",
            "Ichki parvoz Xiva-Toshkent",
            "Ispanzabon professional gid",
            "Barcha kirish chiptalari",
        ],
        "included_ru": [
            "Международный рейс Мадрид-Ташкент (Uzbekistan Airways)",
            "7 ночей в отелях 4*",
            "Все завтраки",
            "Транспорт с кондиционером",
            "Скоростной поезд «Афросиаб»",
            "Внутренний перелёт Хива-Ташкент",
            "Профессиональный испаноговорящий гид",
            "Все входные билеты",
        ],
        "included_en": [
            "International flight Madrid-Tashkent (Uzbekistan Airways)",
            "7 nights in 4* hotels",
            "All breakfasts",
            "AC transport",
            "Afrosiyob high-speed train",
            "Domestic flight Khiva-Tashkent",
            "Professional Spanish-speaking guide",
            "All entrance fees",
        ],
        "included_ko": [
            "국제선 마드리드-타슈켄트 (우즈베키스탄 항공)",
            "4성급 호텔 7박",
            "조식 포함",
            "에어컨 차량",
            "아프로시얍 고속열차",
            "국내선 히바-타슈켄트",
            "전문 스페인어 가이드",
            "모든 입장료",
        ],
        "excluded_uz": ["Vizalar", "Tushlik va kechki ovqat (qo'shimcha)", "Choychaqa", "Foto/video to'lovi"],
        "excluded_ru": ["Визы", "Обеды и ужины (за доплату)", "Чаевые", "Плата за фото/видео"],
        "excluded_en": ["Visas", "Lunches and dinners (supplement)", "Tips", "Photo/video fees"],
        "excluded_ko": ["비자", "중식과 석식 (추가)", "팁", "사진/비디오 촬영비"],
    },
]


# ════════════════════════════════════════════════════════════════════
# COMMAND
# ════════════════════════════════════════════════════════════════════
class Command(BaseCommand):
    help = "Real O'zbekiston tourlarini DBga yozadi (UZ/RU/EN/KO tillarda)"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Avval barcha tour/region/category yozuvlarini o\'chirish')
        parser.add_argument('--regions-only', action='store_true', help='Faqat region va kategoriyalarni seed qilish')

    @transaction.atomic
    def handle(self, *args, **opts):
        # Modellarni dinamik topish — model nomlari farq qilishi mumkin
        try:
            Tour = apps.get_model('tours', 'Tour')
        except LookupError:
            self.stderr.write(self.style.ERROR("tours.Tour modeli topilmadi"))
            return

        try:
            Region = apps.get_model('regions', 'Region')
        except LookupError:
            self.stderr.write(self.style.ERROR("regions.Region modeli topilmadi"))
            return

        Category = None
        for app_label in ['tours', 'categories']:
            try:
                Category = apps.get_model(app_label, 'Category')
                break
            except LookupError:
                continue

        # Translation flag — has modeltranslation if any title_XX field exists
        sample_field_names = {f.name for f in Tour._meta.get_fields()}
        has_modeltranslation = any(
            n.endswith('_uz') or n.endswith('_ru') or n.endswith('_en') or n.endswith('_ko')
            for n in sample_field_names
        )

        if opts['clear']:
            self.stdout.write("Eski yozuvlarni o'chirish...")
            Tour.objects.all().delete()
            Region.objects.all().delete()
            if Category:
                Category.objects.all().delete()

        # ── REGIONS ──────────────────────────────────────────────
        self.stdout.write(self.style.NOTICE("\n🌍 Regionlarni yaratish..."))
        region_objs = {}
        for r in REGIONS_DATA:
            defaults = self._build_defaults(Region, r, ['name', 'description'])
            obj, created = Region.objects.update_or_create(slug=r['slug'], defaults=defaults)
            region_objs[r['slug']] = obj
            mark = "✓ yaratildi" if created else "↺ yangilandi"
            self.stdout.write(f"  {mark}  {r['slug']:20s}  {r['name_uz']}")

        # ── CATEGORIES ───────────────────────────────────────────
        category_objs = {}
        if Category:
            self.stdout.write(self.style.NOTICE("\n📂 Kategoriyalarni yaratish..."))
            for c in CATEGORIES_DATA:
                defaults = self._build_defaults(Category, c, ['name'])
                obj, created = Category.objects.update_or_create(slug=c['slug'], defaults=defaults)
                category_objs[c['slug']] = obj
                mark = "✓" if created else "↺"
                self.stdout.write(f"  {mark}  {c['slug']:15s}  {c['name_uz']}")

        if opts['regions_only']:
            self.stdout.write(self.style.SUCCESS(f"\n✅ {len(region_objs)} region, {len(category_objs)} kategoriya seed qilindi."))
            return

        # ── TOURS ────────────────────────────────────────────────
        self.stdout.write(self.style.NOTICE("\n🧳 Tourlarni yaratish..."))
        for t in TOURS_DATA:
            defaults = self._build_defaults(
                Tour, t,
                fields_with_translation=['name', 'short_description', 'description'],
                skip=['slug', 'region_slug', 'category_slug', 'image_url',
                      'included_uz', 'included_ru', 'included_en', 'included_ko',
                      'excluded_uz', 'excluded_ru', 'excluded_en', 'excluded_ko'],
            )

            # title/name moslamasi
            if 'title' in sample_field_names and 'name' not in sample_field_names:
                defaults['title'] = t.get('name_uz', t['slug'])
                if has_modeltranslation:
                    for lang in ['uz', 'ru', 'en', 'ko']:
                        if f'title_{lang}' in sample_field_names:
                            defaults[f'title_{lang}'] = t.get(f'name_{lang}', '')
                # name maydonlarini olib tashlash
                for k in list(defaults.keys()):
                    if k.startswith('name'):
                        defaults.pop(k, None)

            # Region va kategoriya bog'lanishi
            region = region_objs.get(t['region_slug'])
            if region and 'region' in sample_field_names:
                defaults['region'] = region

            if Category and t.get('category_slug') and 'category' in sample_field_names:
                cat = category_objs.get(t['category_slug'])
                if cat:
                    defaults['category'] = cat

            obj, created = Tour.objects.update_or_create(slug=t['slug'], defaults=defaults)
            mark = "✓ yaratildi" if created else "↺ yangilandi"
            self.stdout.write(f"  {mark}  ${t['price']:>6}  {t['duration_days']}kun  {t['name_uz'][:55]}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ TAYYOR! {len(REGIONS_DATA)} region, {len(CATEGORIES_DATA)} kategoriya, {len(TOURS_DATA)} tour DBga yozildi.\n"
            f"   Saytda ko'rish: http://localhost:8008/uz/tours/\n"
        ))

    def _build_defaults(self, model, data, fields_with_translation=None, skip=None):
        """data dict'dan model fieldlariga mos defaults yasaydi."""
        skip = set(skip or [])
        fields_with_translation = fields_with_translation or []
        model_fields = {f.name for f in model._meta.get_fields()}

        defaults = {}
        for key, val in data.items():
            if key in skip or key == 'slug':
                continue
            # Til-bazadagi maydonlar (name_uz, etc.) — to'g'ridan-to'g'ri
            if key in model_fields:
                defaults[key] = val
        return defaults