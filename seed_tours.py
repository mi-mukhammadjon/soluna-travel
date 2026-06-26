import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from tours.models import Tour, TourCategory, ItineraryDay
from regions.models import Region

# ═══════ 1. REGIONLAR ═══════
regions_data = [
    {'name_uz': 'Toshkent', 'name_ru': 'Ташкент', 'name_en': 'Tashkent', 'slug': 'toshkent', 'description_uz': 'O\'zbekiston poytaxti', 'description_ru': 'Столица Узбекистана', 'description_en': 'Capital of Uzbekistan', 'order': 1},
    {'name_uz': 'Samarqand', 'name_ru': 'Самарканд', 'name_en': 'Samarkand', 'slug': 'samarqand', 'description_uz': 'Buyuk Temur shahri', 'description_ru': 'Город Великого Тимура', 'description_en': 'City of Great Timur', 'order': 2},
    {'name_uz': 'Buxoro', 'name_ru': 'Бухара', 'name_en': 'Bukhara', 'slug': 'buxoro', 'description_uz': 'Muqaddas shahar', 'description_ru': 'Священный город', 'description_en': 'Holy City', 'order': 3},
    {'name_uz': 'Xiva', 'name_ru': 'Хива', 'name_en': 'Khiva', 'slug': 'xiva', 'description_uz': 'Tarixiy shahar', 'description_ru': 'Исторический город', 'description_en': 'Historic City', 'order': 4},
    {'name_uz': 'Farg\'ona', 'name_ru': 'Ферганская область', 'name_en': 'Fergana Valley', 'slug': 'fargona', 'description_uz': 'Vodiy go\'zal tabiati', 'description_ru': 'Красивая природа долины', 'description_en': 'Beautiful valley nature', 'order': 5},
]

created_regions = {}
for rd in regions_data:
    r, _ = Region.objects.get_or_create(slug=rd['slug'], defaults=rd)
    created_regions[rd['slug']] = r
    print(f'Region created: {r.name_uz}')

# ═══════ 2. KATEGORIYALAR ═══════
categories_data = [
    {'name_uz': 'Klassik sayohat', 'name_ru': 'Классическое путешествие', 'name_en': 'Classic Tour', 'slug': 'classic-tour', 'icon': 'road'},
    {'name_uz': 'Ziyorat turizmi', 'name_ru': 'Паломнический туризм', 'name_en': 'Pilgrimage Tour', 'slug': 'pilgrimage-tour', 'icon': 'mosque'},
    {'name_uz': 'Madaniy turizm', 'name_ru': 'Культурный туризм', 'name_en': 'Cultural Tour', 'slug': 'cultural-tour', 'icon': 'landmark'},
]

created_cats = {}
for cd in categories_data:
    c, _ = TourCategory.objects.get_or_create(slug=cd['slug'], defaults=cd)
    created_cats[cd['slug']] = c
    print(f'Category created: {c.name_uz}')

# ═══════ 3. TURLAR ═══════
tours_data = [
    {
        'title_uz': 'Ipak yo\'li',
        'title_ru': 'Шёлковый путь',
        'title_en': 'Silk Road',
        'slug': 'silk-road',
        'category': created_cats['classic-tour'],
        'regions': ['toshkent', 'samarqand', 'buxoro', 'xiva'],
        'short_description_uz': 'O\'zbekistonning eng go\'zal shaharlari orqali 8 kunlik sayohat',
        'short_description_ru': '8-дневное путешествие по самым красивым городам Узбекистана',
        'short_description_en': '8-day journey through the most beautiful cities of Uzbekistan',
        'description_uz': 'Toshkent - Samarqand - Buxoro - Xiva - Urgench marshrutidagi klassik sayohat. Har dushanba kunlari boshlanadi.',
        'description_ru': 'Классическое путешествие по маршруту Ташкент - Самарканд - Бухара - Хива - Ургенч. Начинается каждый понедельник.',
        'description_en': 'Classic tour along Tashkent - Samarkand - Bukhara - Khiva - Urgench route. Starts every Monday.',
        'price': 900,
        'price_uzs': 11700000,
        'duration_days': 8,
        'max_group_size': 30,
        'difficulty': 'easy',
        'includes_uz': '6 tunlik mehmonxona, nonushta, barcha transferlar, kirish chiptalari, gid xizmati, sayohat kartasi va suvenirlar',
        'includes_ru': '6 ночей проживания, завтраки, все трансферы, входные билеты, услуги гида, туристическая карта и сувениры',
        'includes_en': '6 nights accommodation, breakfasts, all transfers, entrance tickets, guide services, tourist map and souvenirs',
        'excludes_uz': 'Xalqaro aviachiptalar, viza, chekinishlar (45 evro), tushlik va kechki ovqat',
        'excludes_ru': 'Международные авиабилеты, виза, чаевые (45 евро), обеды и ужины',
        'excludes_en': 'International flight tickets, visa, tips (45 euros), lunches and dinners',
        'is_active': True,
        'is_featured': True,
    },
    {
        'title_uz': 'Klassik O\'zbekiston',
        'title_ru': 'Классический Узбекистан',
        'title_en': 'Classic Uzbekistan',
        'slug': 'classic-uzbekistan',
        'category': created_cats['classic-tour'],
        'regions': ['toshkent', 'xiva', 'buxoro', 'samarqand'],
        'short_description_uz': 'O\'zbekistonning barcha asosiy shaharlari bilan 8 kunlik tanishuv',
        'short_description_ru': '8-дневное знакомство со всеми основными городами Узбекистана',
        'short_description_en': '8-day acquaintance with all major cities of Uzbekistan',
        'description_uz': 'Toshkent - Urgench - Xiva - Buxoro - Samarqand - Toshkent marshrutidagi to\'liq sayohat. Har shanba kunlari boshlanadi.',
        'description_ru': 'Полное путешествие по маршруту Ташкент - Ургенч - Хива - Бухара - Самарканд - Ташкент. Начинается каждую субботу.',
        'description_en': 'Full journey along Tashkent - Urgench - Khiva - Bukhara - Samarkand - Tashkent route. Starts every Saturday.',
        'price': 1190,
        'price_uzs': 15470000,
        'duration_days': 8,
        'max_group_size': 30,
        'difficulty': 'easy',
        'includes_uz': '7 tunlik mehmonxona, erta kirish, 7 nonushta va 6 tushlik, barcha transferlar, kirish chiptalari, gid',
        'includes_ru': '7 ночей проживания, раннее заселение, 7 завтраков и 6 обедов, все трансферы, входные билеты, гид',
        'includes_en': '7 nights accommodation, early check-in, 7 breakfasts and 6 lunches, all transfers, entrance tickets, guide',
        'excludes_uz': 'Xalqaro aviachiptalar, viza, shaxsiy xarajatlar, chekinishlar (45 evro)',
        'excludes_ru': 'Международные авиабилеты, визовые расходы, личные расходы, чаевые (45 евро)',
        'excludes_en': 'International flight tickets, visa expenses, personal expenses, tips (45 euros)',
        'is_active': True,
        'is_featured': True,
    },
    {
        'title_uz': 'Buxoro pirlarining 7 si',
        'title_ru': '7 Пиров Бухары',
        'title_en': '7 Saints of Bukhara',
        'slug': '7-saints-of-bukhara',
        'category': created_cats['pilgrimage-tour'],
        'regions': ['buxoro'],
        'short_description_uz': 'Buxoro viloyatidagi 7 ta muqaddas ziyoratgohga sayohat',
        'short_description_ru': 'Паломническое путешествие к 7 святым местам Бухарской области',
        'short_description_en': 'Pilgrimage journey to 7 sacred sites of Bukhara region',
        'description_uz': 'Gijduvan, Shafirkan, Vabkent, Romitan, Kagan tumanlaridagi sufiya pirlari qabrlariga ziyorat.',
        'description_ru': 'Паломничество к могилам суфийских пиров в районах Гиждуван, Шафиркан, Вабкент, Ромитан, Каган.',
        'description_en': 'Pilgrimage to Sufi saints tombs in Gijduvan, Shafirkan, Vabkent, Romitan, Kagan districts.',
        'price': 450,
        'price_uzs': 5850000,
        'duration_days': 3,
        'max_group_size': 15,
        'difficulty': 'medium',
        'includes_uz': 'Mehmonxona, nonushta, tushlik, kechki ovqat, transport, gid',
        'includes_ru': 'Проживание, завтрак, обед, ужин, транспорт, гид',
        'includes_en': 'Accommodation, breakfast, lunch, dinner, transport, guide',
        'excludes_uz': 'Shaxsiy xarajatlar, chekinishlar',
        'excludes_ru': 'Личные расходы, чаевые',
        'excludes_en': 'Personal expenses, tips',
        'is_active': True,
        'is_featured': False,
    },
    {
        'title_uz': 'O\'zbekiston — Samarqand bilan',
        'title_ru': 'Узбекистан — Самарканд',
        'title_en': 'Uzbekistan — Samarkand',
        'slug': 'uzbekistan-samarkand',
        'category': created_cats['classic-tour'],
        'regions': ['toshkent', 'xiva', 'buxoro', 'samarqand'],
        'short_description_uz': 'Samarqandda tugaydigan 8 kunlik sayohat',
        'short_description_ru': '8-дневное путешествие, заканчивающееся в Самарканде',
        'short_description_en': '8-day journey ending in Samarkand',
        'description_uz': 'Toshkent - Urgench - Xiva - Buxoro - Samarqand marshrutida sayohat. Samarqandda tugaydi.',
        'description_ru': 'Путешествие по маршруту Ташкент - Ургенч - Хива - Бухара - Самарканд. Заканчивается в Самарканде.',
        'description_en': 'Journey along Tashkent - Urgench - Khiva - Bukhara - Samarkand route. Ends in Samarkand.',
        'price': 1190,
        'price_uzs': 15470000,
        'duration_days': 8,
        'max_group_size': 30,
        'difficulty': 'easy',
        'includes_uz': '7 tunlik mehmonxona, nonushta va tushlik, barcha transferlar, kirish chiptalari, gid',
        'includes_ru': '7 ночей проживания, завтраки и обеды, все трансферы, входные билеты, гид',
        'includes_en': '7 nights accommodation, breakfasts and lunches, all transfers, entrance tickets, guide',
        'excludes_uz': 'Xalqaro aviachiptalar, viza, shaxsiy xarajatlar',
        'excludes_ru': 'Международные авиабилеты, виза, личные расходы',
        'excludes_en': 'International flight tickets, visa, personal expenses',
        'is_active': True,
        'is_featured': False,
    },
]

for td in tours_data:
    regions_slugs = td.pop('regions')
    t, created = Tour.objects.get_or_create(slug=td['slug'], defaults=td)
    if created:
        for slug in regions_slugs:
            if slug in created_regions:
                t.regions.add(created_regions[slug])
        print(f'Tour created: {t.title_ru} (${t.price})')
    else:
        print(f'Tour exists: {t.title_ru}')

# ═══════ 4. ITINERARY DAYS ═══════
silk_road = Tour.objects.get(slug='silk-road')
days_silk = [
    (1, 'Понедельник. Перелёт', 'Вылет в Ташкент, столицу Узбекистана. Ночь на борту самолёта.'),
    (2, 'Вторник. Прибытие в Ташкент', 'Прибытие в аэропорт Ташкента. Прохождение паспортного контроля и встреча с гидом. Завтрак в отеле. Экскурсия по старому городу: комплекс Хаст-Имам, медресе Барак-хана.'),
    (3, 'Среда. Ташкент – Самарканд', 'Переезд в Самарканд. Размещение в гостинице. Экскурсия по площади Регистан и мавзолею Гур-Эмир.'),
    (4, 'Четверг. Самарканд – Бухара', 'Посещение обсерватории Улугбека, архитектурного комплекса Шахи-Зинда, мечети Биби-Ханым. Переезд в Бухару.'),
    (5, 'Пятница. Бухара', 'Экскурсия по Бухаре: мавзолей Саманидов, крепость Арк, ансамбль Пои-Калян, медресе Улугбека и Абдулазиз-хана.'),
    (6, 'Суббота. Бухара – Хива', 'Переезд в Хиву через пустыню Кызылкум. Размещение в гостинице.'),
    (7, 'Воскресенье. Хива', 'Экскурсия по Ичан-Кале: минарет Кальта-Минор, медресе Мухаммад Амин-хана, крепость Куня-Арк, мечеть Джума.'),
    (8, 'Понедельник. Хива – Ургенч', 'Трансфер в аэропорт Ургенча и вылет домой. Окончание программы.'),
]
for day_num, title, desc in days_silk:
    ItineraryDay.objects.get_or_create(tour=silk_road, day=day_num, defaults={'title': title, 'description': desc})

classic_uz = Tour.objects.get(slug='classic-uzbekistan')
days_classic = [
    (1, 'Вылет в Ташкент', 'Вылет из страны проживания в Ташкент. Ночь на борту самолета.'),
    (2, 'Ташкент', 'Прибытие в Ташкент, встреча в аэропорту. Экскурсия по старому городу: комплекс Хаст-Имам, базар Чорсу.'),
    (3, 'Ташкент – Ургенч – Хива', 'Перелет в Ургенч и переезд в Хиву. Осмотр крепости Ичан-Кала (ЮНЕСКО).'),
    (4, 'Хива – Бухара', 'Переезд в Бухару (около 450 км). Размещение в гостинице.'),
    (5, 'Бухара', 'Экскурсия по Бухаре: мавзолей Саманидов, крепость Арк, ансамбль Ляби-Хауз.'),
    (6, 'Бухара – Самарканд', 'Переезд в Самарканд. Посещение обсерватории Улугбека, площади Регистан.'),
    (7, 'Самарканд – Ташкент', 'Комплекс Шахи-Зинда, мечеть Биби-Ханым. Переезд на поезде в Ташкент.'),
    (8, 'Вылет домой', 'Трансфер в аэропорт и завершение обслуживания.'),
]
for day_num, title, desc in days_classic:
    ItineraryDay.objects.get_or_create(tour=classic_uz, day=day_num, defaults={'title': title, 'description': desc})

print()
print(f'Total tours: {Tour.objects.count()}')
print(f'Total regions: {Region.objects.count()}')
print(f'Total categories: {TourCategory.objects.count()}')
print(f'Total itinerary days: {ItineraryDay.objects.count()}')
