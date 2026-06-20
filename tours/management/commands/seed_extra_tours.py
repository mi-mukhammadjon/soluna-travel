"""
Qo'shimcha tour (TAS-SKD) va qolgan tourlar uchun itinerary'larni qo'shadi.

Joylash: tours/management/commands/seed_extra_tours.py

Ishlatish:
  docker compose exec web python manage.py seed_extra_tours

ESLATMA: Avval `seed_real_tours` ishlatilgan bo'lishi kerak.
Bu command MAVJUDLARNI O'CHIRMAYDI — faqat yangilarini qo'shadi va itinerary'larni to'ldiradi.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps


# ════════════════════════════════════════════════════════════════════
# YANGI TOUR — TAS-SKD variant (Samarqandda tugaydi)
# ════════════════════════════════════════════════════════════════════
EXTRA_TOUR = {
    "slug": "classic-uzbekistan-tas-skd-8d",
    "name_uz": "Klassik O'zbekiston — Samarqandda yakun (TAS-SKD)",
    "name_ru": "Классический Узбекистан — Финиш в Самарканде (TAS-SKD)",
    "name_en": "Classic Uzbekistan — Ending in Samarkand (TAS-SKD)",
    "name_ko": "클래식 우즈베키스탄 — 사마르칸트에서 종료 (TAS-SKD)",

    "short_description_uz": "8 kun / 7 tun. Toshkentdan boshlanib, Samarqand aeroportidan jo'nash. Tezyurar poyezdsiz, ko'proq vaqt Samarqandda.",
    "short_description_ru": "8 дней / 7 ночей. Старт из Ташкента, вылет из Самарканда. Без обратного поезда — больше времени в Самарканде.",
    "short_description_en": "8 days / 7 nights. Starts in Tashkent, departs from Samarkand. No return train — more time in Samarkand.",
    "short_description_ko": "8일 / 7박. 타슈켄트에서 시작, 사마르칸트에서 출발. 귀환 기차 없음 — 사마르칸트에서 더 많은 시간.",

    "description_uz": """Toshkent-Samarqand yo'nalishidagi guruh turi.

Marshrut: Toshkent – Urganch – Xiva – Buxoro – Samarqand
Jo'nashlar: Har shanba
Eng kam: 2 ishtirokchi

TAS-TAS variantidan farqi: Tur Samarqandda tugaydi va u yerdan to'g'ridan-to'g'ri uchish mumkin. Toshkent–Samarqand poyezd chiptasi kerak emas, narx bir xil.

Qo'shimcha ekskursiyalar:
• Usmon Qur'oni muzeyiga ekskursiya — 40 USD
• "Happy Hour" — quyosh botishida vino — 10 USD""",

    "description_ru": """Групповой тур с финишем в Самарканде.

Маршрут: Ташкент – Ургенч – Хива – Бухара – Самарканд
Заезды: каждую субботу
Минимум: 2 участника

Отличие от TAS-TAS: тур заканчивается в Самарканде с возможностью прямого вылета. Билет на поезд Самарканд-Ташкент не нужен, цена та же.

Дополнительные экскурсии:
• Музей Корана Османа — 40 USD
• «Happy Hour» — бокал вина на закате — 10 USD""",

    "description_en": """Group tour ending in Samarkand.

Route: Tashkent – Urgench – Khiva – Bukhara – Samarkand
Departures: Every Saturday
Minimum: 2 participants

Difference from TAS-TAS: tour ends in Samarkand with direct flight option. No need for Samarkand-Tashkent train, same price.

Optional excursions:
• Quran of Uthman Museum — $40
• "Happy Hour" — glass of wine at sunset — $10""",

    "description_ko": """사마르칸트에서 종료되는 그룹 투어.

루트: 타슈켄트 – 우르겐치 – 히바 – 부하라 – 사마르칸트
출발: 매주 토요일
최소: 2명

TAS-TAS 와 차이: 투어는 사마르칸트에서 종료되어 직항편 이용 가능. 사마르칸트-타슈켄트 기차표 불필요, 가격 동일.

선택 관광:
• 우스만 쿠란 박물관 — $40
• "해피아워" — 일몰의 와인 한잔 — $10""",

    "price": Decimal("1190"),
    "single_supplement": Decimal("200"),
    "duration_days": 8,
    "duration_nights": 7,
    "min_people": 2,
    "max_people": 16,
    "rating": Decimal("4.91"),
    "review_count": 342,
    "tour_type": "Cultural",
    "is_featured": True,
    "category_slug": "classic",
    "region_slug": "samarkand",
    "image_url": "https://images.unsplash.com/photo-1559564484-0a8caa9e4d05?w=1200",

    "included_uz": [
        "Ikki kishilik xonada 7 tun joylashish",
        "Erta joylashish (kelish kuni)",
        "7 nonushta va 6 tushlik",
        "Tushlik vaqtida choy va suv",
        "Barcha transferlar va konditsionerli transport",
        "Dasturdagi kirish chiptalari",
        "Ichki parvoz Toshkent – Urganch",
        "Gid xizmati",
    ],
    "included_ru": [
        "Проживание 7 ночей в двухместном номере",
        "Раннее заселение в день прибытия",
        "7 завтраков и 6 обедов",
        "Чай и вода во время обедов",
        "Все трансферы и транспорт с кондиционером",
        "Входные билеты по программе",
        "Внутренний авиаперелёт Ташкент – Ургенч",
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
        "Guide services",
    ],
    "included_ko": [
        "더블룸 7박 숙박",
        "도착일 얼리 체크인",
        "조식 7회, 중식 6회",
        "중식 시 차와 물",
        "모든 트랜스퍼와 에어컨 차량",
        "프로그램별 입장료",
        "국내선 타슈켄트 – 우르겐치",
        "가이드 서비스",
    ],
    "excluded_uz": ["Xalqaro aviachiptalar", "Vizalar", "Ichimliklar va shaxsiy xarajatlar",
                    "Foto/video to'lovi muzeylarda", "Choychaqa (45 EUR majburiy)"],
    "excluded_ru": ["Международные авиабилеты", "Визовые расходы", "Напитки и личные расходы",
                    "Фото-видеосборы в музеях", "Чаевые (45 EUR обязательно)"],
    "excluded_en": ["International flights", "Visa fees", "Drinks and personal expenses",
                    "Photo/video fees at museums", "Tips ($45 EUR mandatory)"],
    "excluded_ko": ["국제 항공권", "비자 비용", "음료와 개인 비용",
                    "박물관 사진/비디오 촬영비", "팁 (45 EUR 필수)"],
}


# ════════════════════════════════════════════════════════════════════
# ITINERARIES — qolgan 4 ta tour uchun
# ════════════════════════════════════════════════════════════════════
EXTRA_ITINERARIES = {

    # ── Classic Uzbekistan TAS-TAS ────────────────────────────────
    "classic-uzbekistan-tas-tas-8d": [
        {
            "day": 1, "title_uz": "Toshkentga uchish", "title_ru": "Вылет в Ташкент",
            "title_en": "Flight to Tashkent", "title_ko": "타슈켄트행 비행",
            "description_uz": "Yashash mamlakatidan Toshkentga uchish. Samolyot bortida tunash.",
            "description_ru": "Вылет из страны проживания в Ташкент. Ночь на борту самолёта.",
            "description_en": "Flight from home country to Tashkent. Overnight on board.",
            "description_ko": "거주국에서 타슈켄트행 비행. 기내에서 숙박.",
        },
        {
            "day": 2, "title_uz": "Toshkent", "title_ru": "Ташкент",
            "title_en": "Tashkent", "title_ko": "타슈켄트",
            "description_uz": "Aeroportda kutib olish, erta joylashish. Eski shahar bo'ylab ekskursiya: Xast-Imom majmuasi, Baroqxon madrasasi, Tilla-Shayx masjidi, Chorsu bozori. Tushlikdan keyin zamonaviy Toshkent: Mustaqillik maydoni, Ikkinchi jahon urushi memoriali, Romanovlar saroyi, Opera maydoni, Amir Temur xiyoboni.",
            "description_ru": "Встреча в аэропорту, раннее заселение. Экскурсия по старому городу: комплекс Хаст-Имам, медресе Барак-хана, мечеть Тилля-Шейх, базар Чорсу. После обеда — современный Ташкент: площадь Независимости, мемориал Второй мировой, дворец Романовых, площадь Оперы, сквер Амира Темура.",
            "description_en": "Airport meet, early check-in. Old city tour: Khast-Imam complex, Barak-Khan madrasah, Tilla-Sheikh mosque, Chorsu bazaar. After lunch — modern Tashkent: Independence Square, WWII memorial, Romanov Palace, Opera Square, Amir Temur square.",
            "description_ko": "공항 미팅, 얼리 체크인. 구시가지 투어: 하스트이맘 단지, 바라크칸 마드라사, 틸라셰이크 모스크, 초르수 시장. 중식 후 — 현대 타슈켄트: 독립광장, 2차대전 기념관, 로마노프 궁전, 오페라 광장, 아미르 티무르 광장.",
        },
        {
            "day": 3, "title_uz": "Toshkent – Urganch – Xiva", "title_ru": "Ташкент – Ургенч – Хива",
            "title_en": "Tashkent – Urgench – Khiva", "title_ko": "타슈켄트 – 우르겐치 – 히바",
            "description_uz": "Urganchga parvoz va Xivaga o'tish. Ichan-Qal'a qal'asi (UNESCO): Kalta-Minor minorasi, Muhammad Aminxon madrasasi, Juma masjidi, Pahlavon Mahmud maqbarasi, Toshhovli saroyi.",
            "description_ru": "Перелёт в Ургенч и переезд в Хиву. Крепость Ичан-Кала (ЮНЕСКО): минарет Кальта-Минор, медресе Мухаммад Амин-хана, мечеть Джума, мавзолей Пахлавана Махмуда, дворец Таш-Ховли.",
            "description_en": "Flight to Urgench and drive to Khiva. Ichan-Kala fortress (UNESCO): Kalta-Minor minaret, Mohammed Amin Khan madrasah, Juma mosque, Pahlavan Mahmud mausoleum, Tash-Hauli palace.",
            "description_ko": "우르겐치행 비행과 히바로 이동. 이찬칼라 요새 (유네스코): 칼타미노르 미나레트, 무함마드 아민 칸 마드라사, 주마 모스크, 팔라반 마무드 영묘, 타시하울리 궁전.",
        },
        {
            "day": 4, "title_uz": "Xiva – Buxoro", "title_ru": "Хива – Бухара",
            "title_en": "Khiva – Bukhara", "title_ko": "히바 – 부하라",
            "description_uz": "Buxoroga o'tish (~450 km, 7-7,5 soat). Yo'lda tushlik / lunch box. Mehmonxonada joylashish.",
            "description_ru": "Переезд в Бухару (около 450 км, 7–7,5 часов). Обед по дороге/lunch box. Размещение.",
            "description_en": "Drive to Bukhara (~450 km, 7-7.5 hours). Lunch en route / lunch box. Hotel check-in.",
            "description_ko": "부하라로 이동 (약 450km, 7-7.5시간). 도중 중식 / 도시락. 호텔 체크인.",
        },
        {
            "day": 5, "title_uz": "Buxoro", "title_ru": "Бухара",
            "title_en": "Bukhara", "title_ko": "부하라",
            "description_uz": "Buxoro ekskursiyasi (UNESCO): Somoniylar maqbarasi, Chashma-Ayub, Bolo-Hovuz masjidi, Ark qal'asi, Labi-Hovuz ansambli, Ko'kaldosh madrasasi, savdo gumbazlari, Ulug'bek va Abdulazizxon madrasalari, Po'i-Kalon majmuasi.",
            "description_ru": "Экскурсия по Бухаре (ЮНЕСКО): мавзолей Саманидов, Чашма-Аюб, мечеть Боло-Хауз, крепость Арк, ансамбль Ляби-Хауз, медресе Кукельдаш, торговые купола, медресе Улугбека и Абдулазиз-хана, комплекс Пои-Калян.",
            "description_en": "Bukhara tour (UNESCO): Samanid mausoleum, Chashma-Ayub, Bolo-Hauz mosque, Ark fortress, Lyab-i-Hauz ensemble, Kukeldash madrasah, trading domes, Ulugh Beg & Abdulaziz-Khan madrasahs, Poi-Kalyan complex.",
            "description_ko": "부하라 투어 (유네스코): 사마니드 영묘, 차슈마-아유브, 볼로하우즈 모스크, 아르크 요새, 라비하우즈 단지, 쿠켈다시 마드라사, 무역 돔, 울루그벡 & 압둘아지즈 칸 마드라사, 포이칼란 단지.",
        },
        {
            "day": 6, "title_uz": "Buxoro – Samarqand", "title_ru": "Бухара – Самарканд",
            "title_en": "Bukhara – Samarkand", "title_ko": "부하라 – 사마르칸트",
            "description_uz": "Samarqandga o'tish. Ulug'bek rasadxonasi, Go'ri Amir maqbarasi va Registon maydoni (Ulug'bek, Sherdor, Tillakori madrasalari). Kechqurun yoritilgan Registonga tashqi qarash.",
            "description_ru": "Переезд в Самарканд. Обсерватория Улугбека, мавзолей Гур-Эмир, площадь Регистан (медресе Улугбека, Шер-Дор, Тилля-Кари). Вечером внешний осмотр Регистана в подсветке.",
            "description_en": "Drive to Samarkand. Ulugh Beg observatory, Gur-e-Amir mausoleum, Registan Square (Ulugh Beg, Sher-Dor, Tilla-Kari madrasahs). Evening — external view of illuminated Registan.",
            "description_ko": "사마르칸트로 이동. 울루그벡 천문대, 구르 에미르 영묘, 레기스탄 광장 (울루그벡, 셰르도르, 틸라카리 마드라사). 저녁 — 조명이 켜진 레기스탄 외부 관람.",
        },
        {
            "day": 7, "title_uz": "Samarqand – Toshkent", "title_ru": "Самарканд – Ташкент",
            "title_en": "Samarkand – Tashkent", "title_ko": "사마르칸트 – 타슈켄트",
            "description_uz": "'Meros' qog'oz fabrikasi, Shohi-Zinda majmuasi, Bibi-Xonim masjidi va Siyob bozori. Tushlikdan keyin tezyurar poyezdda Toshkentga. Mehmonxonada joylashish.",
            "description_ru": "Фабрика бумаги «Мерос», комплекс Шахи-Зинда, мечеть Биби-Ханым и базар Сиаб. После обеда — скоростной поезд в Ташкент. Размещение в отеле.",
            "description_en": "Meros paper factory, Shah-i-Zinda complex, Bibi-Khanym mosque and Siab bazaar. After lunch — high-speed train to Tashkent. Hotel check-in.",
            "description_ko": "메로스 종이 공장, 샤히진다 단지, 비비하늠 모스크와 시압 시장. 중식 후 — 타슈켄트행 고속열차. 호텔 체크인.",
        },
        {
            "day": 8, "title_uz": "Vatanga uchish", "title_ru": "Вылет домой",
            "title_en": "Departure home", "title_ko": "귀국",
            "description_uz": "Aeroportga transfer va xizmat ko'rsatishning yakuni.",
            "description_ru": "Трансфер в аэропорт и завершение обслуживания.",
            "description_en": "Airport transfer and end of services.",
            "description_ko": "공항 트랜스퍼와 서비스 종료.",
        },
    ],

    # ── Silk Road 8 kun ───────────────────────────────────────────
    "silk-road-uzbekistan-8d": [
        {
            "day": 1, "title_uz": "Dushanba — Uchish", "title_ru": "Понедельник — Перелёт",
            "title_en": "Monday — Flight", "title_ko": "월요일 — 비행",
            "description_uz": "O'zbekistonning poytaxti Toshkentga uchish. Samolyot bortida tunash.",
            "description_ru": "Вылет в Ташкент, столицу Узбекистана. Ночь на борту самолёта.",
            "description_en": "Flight to Tashkent, capital of Uzbekistan. Overnight on board.",
            "description_ko": "우즈베키스탄 수도 타슈켄트로 비행. 기내 숙박.",
        },
        {
            "day": 2, "title_uz": "Seshanba — Toshkentga kelish", "title_ru": "Вторник — Прибытие в Ташкент",
            "title_en": "Tuesday — Arrival Tashkent", "title_ko": "화요일 — 타슈켄트 도착",
            "description_uz": "Toshkent aeroportiga kelish. Pasport nazoratidan o'tish va gid bilan uchrashish. Mehmonxonada nonushta. Eski shahar bo'ylab ekskursiya: Xast-Imom majmuasi, Baroqxon madrasasi, Kafal Shoshiy madrasasi, Tilla-Shayx masjidi, Usmon Qur'oni muzeyi va Chorsu bozori. Zamonaviy Toshkent ekskursiyasi: Mustaqillik maydoni, Romanovlar saroyi (tashqi), Navoiy opera teatri, Amir Temur xiyoboni.",
            "description_ru": "Прибытие в аэропорт Ташкента. Паспортный контроль и встреча с гидом. Завтрак в отеле. Экскурсия по старому городу: комплекс Хаст-Имам, медресе Барак-хана, медресе Кафал Шаши, мечеть Тилля-Шейх, музей Корана Османа и базар Чорсу. Современный Ташкент: площадь Независимости, дворец Романовых (внешний осмотр), театр оперы и балета Навои, площадь Амира Темура.",
            "description_en": "Arrival at Tashkent airport. Passport control and meeting with guide. Breakfast at hotel. Old city tour: Khast-Imam complex, Barak-Khan madrasah, Kaffal Shashi madrasah, Tilla-Sheikh mosque, Quran of Uthman museum, and Chorsu bazaar. Modern Tashkent: Independence Square, Romanov Palace (external), Navoi Opera Theatre, Amir Temur square.",
            "description_ko": "타슈켄트 공항 도착. 입국 심사 후 가이드 미팅. 호텔 조식. 구시가지 투어: 하스트이맘 단지, 바라크칸 마드라사, 카팔샤시 마드라사, 틸라셰이크 모스크, 우스만 쿠란 박물관, 초르수 시장. 현대 타슈켄트: 독립광장, 로마노프 궁전 (외부), 나보이 오페라 극장, 아미르 티무르 광장.",
        },
        {
            "day": 3, "title_uz": "Chorshanba — Toshkent – Samarqand", "title_ru": "Среда — Ташкент – Самарканд",
            "title_en": "Wednesday — Tashkent – Samarkand", "title_ko": "수요일 — 타슈켄트 – 사마르칸트",
            "description_uz": "Samarqandga o'tish. Mehmonxonada joylashish. Registon maydoni ekskursiyasi (Ulug'bek, Sherdor va Tillakori madrasalari) va Amir Temur va oilasining maqbarasi — Go'ri Amir.",
            "description_ru": "Переезд в Самарканд. Размещение в гостинице. Экскурсия по площади Регистан (медресе Улугбека, Шер-Дор и Тилля-Кари) и мавзолею Гур-Эмир — усыпальнице Амира Темура и членов его семьи.",
            "description_en": "Drive to Samarkand. Hotel check-in. Registan Square tour (Ulugh Beg, Sher-Dor, Tilla-Kari madrasahs) and Gur-e-Amir mausoleum — tomb of Amir Temur and his family.",
            "description_ko": "사마르칸트로 이동. 호텔 체크인. 레기스탄 광장 투어 (울루그벡, 셰르도르, 틸라카리 마드라사)와 구르 에미르 영묘 — 아미르 티무르와 그의 가족 묘.",
        },
        {
            "day": 4, "title_uz": "Payshanba — Samarqand – Buxoro", "title_ru": "Четверг — Самарканд – Бухара",
            "title_en": "Thursday — Samarkand – Bukhara", "title_ko": "목요일 — 사마르칸트 – 부하라",
            "description_uz": "Ulug'bek rasadxonasi va muzeyi, Shohi-Zinda majmuasi, Bibi-Xonim masjidi va Siyob bozori. Buxoroga o'tish va mehmonxonada joylashish.",
            "description_ru": "Обсерватория Улугбека и музей, архитектурный комплекс Шахи-Зинда, мечеть Биби-Ханым и базар Сиаб. Переезд в Бухару и размещение в гостинице.",
            "description_en": "Ulugh Beg observatory and museum, Shah-i-Zinda complex, Bibi-Khanym mosque and Siab bazaar. Drive to Bukhara and hotel check-in.",
            "description_ko": "울루그벡 천문대와 박물관, 샤히진다 단지, 비비하늠 모스크와 시압 시장. 부하라로 이동, 호텔 체크인.",
        },
        {
            "day": 5, "title_uz": "Juma — Buxoro", "title_ru": "Пятница — Бухара",
            "title_en": "Friday — Bukhara", "title_ko": "금요일 — 부하라",
            "description_uz": "Buxoro ekskursiyasi: Somoniylar maqbarasi, Chashma-Ayub maqbarasi va muqaddas buloq, Bolo-Hovuz masjidi, Ark qal'asi, Po'i-Kalon majmuasi, XVI asr savdo gumbazlari, Ulug'bek va Abdulazizxon madrasalari, Labi-Hovuz ansambli va Magoki-Attori masjidi.",
            "description_ru": "Экскурсия по Бухаре: мавзолей Саманидов, мавзолей и святой источник Чашма-Аюб, мечеть Боло-Хауз, крепость Арк, ансамбль Пои-Калян, торговые купола XVI века, медресе Улугбека и Абдулазиз-хана, ансамбль Ляби-Хауз и мечеть Магоки-Аттори.",
            "description_en": "Bukhara tour: Samanid mausoleum, Chashma-Ayub mausoleum and holy spring, Bolo-Hauz mosque, Ark fortress, Poi-Kalyan complex, 16th-century trading domes, Ulugh Beg and Abdulaziz-Khan madrasahs, Lyab-i-Hauz ensemble, Magoki-Attori mosque.",
            "description_ko": "부하라 투어: 사마니드 영묘, 차슈마-아유브 영묘와 성스러운 샘, 볼로하우즈 모스크, 아르크 요새, 포이칼란 단지, 16세기 무역 돔, 울루그벡과 압둘아지즈 칸 마드라사, 라비하우즈 단지, 마고키-아토리 모스크.",
        },
        {
            "day": 6, "title_uz": "Shanba — Buxoro – Xiva", "title_ru": "Суббота — Бухара – Хива",
            "title_en": "Saturday — Bukhara – Khiva", "title_ko": "토요일 — 부하라 – 히바",
            "description_uz": "Qizilqum cho'li orqali Xivaga o'tish. Mehmonxonada joylashish.",
            "description_ru": "Переезд в Хиву через пустыню Кызылкум. Размещение в гостинице.",
            "description_en": "Drive to Khiva through the Kyzylkum desert. Hotel check-in.",
            "description_ko": "키질쿰 사막을 통해 히바로 이동. 호텔 체크인.",
        },
        {
            "day": 7, "title_uz": "Yakshanba — Xiva", "title_ru": "Воскресенье — Хива",
            "title_en": "Sunday — Khiva", "title_ko": "일요일 — 히바",
            "description_uz": "Ichan-Qal'a ekskursiyasi: Kalta-Minor minorasi, Muhammad Aminxon madrasasi, Muhammad Rahimxon madrasasi, Kunya-Ark qal'asi, Juma masjidi, Islom-Xo'ja minorasi va madrasasi, Pahlavon Mahmud maqbarasi, Allaqulixon karvonsaroyi va Toshhovli saroyi.",
            "description_ru": "Экскурсия по Ичан-Кале: минарет Кальта-Минор, медресе Мухаммад Амин-хана, медресе Мухаммад Рахим-хана, крепость Куня-Арк, мечеть Джума, минарет и медресе Ислам-Ходжи, мавзолей Пахлавана Махмуда, караван-сарай Аллакули-хана и дворец Таш-Ховли.",
            "description_en": "Ichan-Kala tour: Kalta-Minor minaret, Mohammed Amin Khan madrasah, Mohammed Rahim Khan madrasah, Kunya-Ark fortress, Juma mosque, Islam-Khoja minaret and madrasah, Pahlavan Mahmud mausoleum, Allakuli Khan caravanserai, Tash-Hauli palace.",
            "description_ko": "이찬칼라 투어: 칼타미노르 미나레트, 무함마드 아민 칸 마드라사, 무함마드 라힘 칸 마드라사, 쿠냐-아르크 요새, 주마 모스크, 이슬람-호자 미나레트와 마드라사, 팔라반 마무드 영묘, 알라쿨리 칸 카라반세라이, 타시하울리 궁전.",
        },
        {
            "day": 8, "title_uz": "Dushanba — Xiva – Urganch ✈ Uy", "title_ru": "Понедельник — Хива – Ургенч ✈ Домой",
            "title_en": "Monday — Khiva – Urgench ✈ Home", "title_ko": "월요일 — 히바 – 우르겐치 ✈ 귀국",
            "description_uz": "Urganch aeroportiga transfer va uyga uchish. Dasturning yakuni.",
            "description_ru": "Трансфер в аэропорт Ургенча и вылет домой. Окончание программы.",
            "description_en": "Transfer to Urgench airport and flight home. End of program.",
            "description_ko": "우르겐치 공항 트랜스퍼와 귀국 비행. 프로그램 종료.",
        },
    ],

    # ── Premium Spanish 8 kun ─────────────────────────────────────
    "uzbekistan-premium-spanish-8d": [
        {
            "day": 1, "title_uz": "Madrid → Toshkent", "title_ru": "Мадрид → Ташкент",
            "title_en": "Madrid → Tashkent", "title_ko": "마드리드 → 타슈켄트",
            "description_uz": "18:35 Madriddan Toshkentga uchish (Uzbekistan Airways HY242). Bortida tunash.",
            "description_ru": "18:35 Вылет из Мадрида в Ташкент (Uzbekistan Airways HY242). Ночь на борту.",
            "description_en": "18:35 Departure from Madrid to Tashkent (Uzbekistan Airways HY242). Overnight on board.",
            "description_ko": "18:35 마드리드에서 타슈켄트로 출발 (우즈베키스탄 항공 HY242). 기내 숙박.",
        },
        {
            "day": 2, "title_uz": "Toshkentga kelish", "title_ru": "Прибытие в Ташкент",
            "title_en": "Arrival in Tashkent", "title_ko": "타슈켄트 도착",
            "description_uz": "04:40 Toshkent xalqaro aeroportiga qo'nish (HY242). Pasport nazoratidan o'tish va gid bilan uchrashish. ~07:00 mehmonxonaga transfer va nonushta. Eski shahar ekskursiyasi: Xast-Imom majmuasi (XVI-XVII), Baroqxon madrasasi, Kafal Shoshiy madrasasi, Tilla-Shayx masjidi va Usmon Qur'oni muzeyi, Chorsu bozori. Zamonaviy Toshkent: Mustaqillik maydoni, Romanovlar saroyi, Opera maydoni, Amir Temur xiyoboni.",
            "description_ru": "04:40 Прибытие в аэропорт Ташкента (HY242). Паспортный контроль и встреча с гидом. ~07:00 трансфер в отель и завтрак. Экскурсия по старому городу: комплекс Хаст-Имам (XVI-XVII), медресе Барак-хана, Кафал Шаши, мечеть Тилля-Шейх и музей Корана Османа, базар Чорсу. Современный Ташкент: площадь Независимости, дворец Романовых, площадь Оперы, сквер Амира Темура.",
            "description_en": "04:40 Arrival at Tashkent international airport (HY242). Passport control and meeting with guide. ~07:00 transfer to hotel and breakfast. Old city tour: Khast-Imam complex (16th-17th c.), Barak-Khan madrasah, Kaffal Shashi, Tilla-Sheikh mosque, Quran of Uthman museum, Chorsu bazaar. Modern Tashkent: Independence Square, Romanov Palace, Opera Square, Amir Temur square.",
            "description_ko": "04:40 타슈켄트 국제공항 도착 (HY242). 입국 심사와 가이드 미팅. ~07:00 호텔 트랜스퍼와 조식. 구시가지 투어: 하스트이맘 단지 (16-17세기), 바라크칸 마드라사, 카팔샤시, 틸라셰이크 모스크와 우스만 쿠란 박물관, 초르수 시장. 현대 타슈켄트: 독립광장, 로마노프 궁전, 오페라 광장, 아미르 티무르 광장.",
        },
        {
            "day": 3, "title_uz": "Toshkent → Samarqand", "title_ru": "Ташкент → Самарканд",
            "title_en": "Tashkent → Samarkand", "title_ko": "타슈켄트 → 사마르칸트",
            "description_uz": "Samarqandga ketish (350 km, 5 soat) yoki ixtiyoriy Afrosiyob/Sharq tezyurar poyezdi. Mehmonxonada joylashish. Mashhur shahar bo'ylab ekskursiya: Registon maydoni — uchta katta madrasa (Ulug'bek XV asr, Sherdor XVII asr, Tillakori XVII asr); Go'ri Amir maqbarasi — Amir Temur va oilasining maqbarasi.",
            "description_ru": "Переезд в Самарканд (350 км, 5 ч) или опциональный поезд «Афросиаб/Шарк». Размещение. Экскурсия по легендарному городу: площадь Регистан с тремя медресе (Улугбек XV, Шер-Дор XVII, Тилля-Кари XVII); мавзолей Гур-Эмир — усыпальница Тамерлана и его семьи.",
            "description_en": "Drive to Samarkand (350 km, 5 hrs) or optional Afrosiyob/Sharq high-speed train. Hotel check-in. Legendary city tour: Registan Square with three madrasahs (Ulugh Beg 15th c., Sher-Dor 17th c., Tilla-Kari 17th c.); Gur-e-Amir mausoleum — tomb of Tamerlane and his family.",
            "description_ko": "사마르칸트로 이동 (350km, 5시간) 또는 아프로시얍/샤르크 고속열차 옵션. 호텔 체크인. 전설의 도시 투어: 레기스탄 광장의 세 마드라사 (울루그벡 15세기, 셰르도르 17세기, 틸라카리 17세기); 구르 에미르 영묘 — 티무르와 그의 가족 묘.",
        },
        {
            "day": 4, "title_uz": "Samarqand → Buxoro", "title_ru": "Самарканд → Бухара",
            "title_en": "Samarkand → Bukhara", "title_ko": "사마르칸트 → 부하라",
            "description_uz": "Ulug'bek rasadxonasi (XV asr) va muzeyi — Ulug'bek Amir Temurning nabirasi, jahonga mashhur astronom. Shohi-Zinda majmuasi (IX-XV asr) — payg'ambar Muhammadning amakivachchasi Qusam ibn Abbosning maqbarasi. Bibi-Xonim masjidi (XV asr) va Siyob bozori. Buxoroga o'tish (260 km, 5 soat).",
            "description_ru": "Обсерватория Улугбека (XV в.) и музей — Улугбек, внук Тамерлана, известный астроном. Комплекс Шахи-Зинда (IX-XV вв.) — место паломничества, гробница Кусам ибн Аббаса. Мечеть Биби-Ханым (XV в.) и базар Сиаб. Переезд в Бухару (260 км, 5 ч).",
            "description_en": "Ulugh Beg observatory (15th c.) and museum — Ulugh Beg, grandson of Tamerlane, eminent astronomer. Shah-i-Zinda complex (9th-15th c.) — pilgrimage site, tomb of Qusam ibn Abbas. Bibi-Khanym mosque (15th c.) and Siab bazaar. Drive to Bukhara (260 km, 5 hrs).",
            "description_ko": "울루그벡 천문대 (15세기)와 박물관 — 티무르의 손자 울루그벡, 저명한 천문학자. 샤히진다 단지 (9-15세기) — 순례지, 쿠삼 이븐 아바스의 묘. 비비하늠 모스크 (15세기)와 시압 시장. 부하라로 이동 (260km, 5시간).",
        },
        {
            "day": 5, "title_uz": "Buxoro", "title_ru": "Бухара",
            "title_en": "Bukhara", "title_ko": "부하라",
            "description_uz": "To'liq kun Buxoroda: Somoniylar maqbarasi, Chashma-Ayub, Bolo-Hovuz masjidi, Ark qal'asi, Po'i-Kalon majmuasi (Kalon minorasi, Kalon masjidi, Mir-Arab madrasasi), savdo gumbazlari, Labi-Hovuz ansambli, Ko'kaldosh madrasasi.",
            "description_ru": "Полный день в Бухаре: мавзолей Саманидов, Чашма-Аюб, мечеть Боло-Хауз, крепость Арк, комплекс Пои-Калян (минарет, мечеть, медресе Мири-Араб), торговые купола, ансамбль Ляби-Хауз, медресе Кукельдаш.",
            "description_en": "Full day in Bukhara: Samanid mausoleum, Chashma-Ayub, Bolo-Hauz mosque, Ark fortress, Poi-Kalyan complex (Kalyan minaret and mosque, Mir-i-Arab madrasah), trading domes, Lyab-i-Hauz ensemble, Kukeldash madrasah.",
            "description_ko": "부하라 종일: 사마니드 영묘, 차슈마-아유브, 볼로하우즈 모스크, 아르크 요새, 포이칼란 단지 (칼란 미나레트와 모스크, 미리-아랍 마드라사), 무역 돔, 라비하우즈 단지, 쿠켈다시 마드라사.",
        },
        {
            "day": 6, "title_uz": "Buxoro → Xiva", "title_ru": "Бухара → Хива",
            "title_en": "Bukhara → Khiva", "title_ko": "부하라 → 히바",
            "description_uz": "Qizilqum cho'li orqali Xivaga o'tish (~450 km, 7-8 soat). Mehmonxonada joylashish.",
            "description_ru": "Переезд в Хиву через пустыню Кызылкум (~450 км, 7-8 часов). Размещение в гостинице.",
            "description_en": "Drive to Khiva through the Kyzylkum desert (~450 km, 7-8 hours). Hotel check-in.",
            "description_ko": "키질쿰 사막을 통해 히바로 이동 (~450km, 7-8시간). 호텔 체크인.",
        },
        {
            "day": 7, "title_uz": "Xiva", "title_ru": "Хива",
            "title_en": "Khiva", "title_ko": "히바",
            "description_uz": "Ichan-Qal'a ekskursiyasi: Kalta-Minor minorasi, Muhammad Aminxon madrasasi, Kunya-Ark, Juma masjidi, Islom-Xo'ja minorasi va madrasasi, Pahlavon Mahmud maqbarasi, Toshhovli saroyi.",
            "description_ru": "Экскурсия по Ичан-Кале: минарет Кальта-Минор, медресе Мухаммад Амин-хана, Куня-Арк, мечеть Джума, минарет и медресе Ислам-Ходжи, мавзолей Пахлавана Махмуда, дворец Таш-Ховли.",
            "description_en": "Ichan-Kala tour: Kalta-Minor minaret, Mohammed Amin Khan madrasah, Kunya-Ark, Juma mosque, Islam-Khoja minaret and madrasah, Pahlavan Mahmud mausoleum, Tash-Hauli palace.",
            "description_ko": "이찬칼라 투어: 칼타미노르 미나레트, 무함마드 아민 칸 마드라사, 쿠냐-아르크, 주마 모스크, 이슬람-호자 미나레트와 마드라사, 팔라반 마무드 영묘, 타시하울리 궁전.",
        },
        {
            "day": 8, "title_uz": "Xiva → Urganch ✈ Madrid", "title_ru": "Хива → Ургенч ✈ Мадрид",
            "title_en": "Khiva → Urgench ✈ Madrid", "title_ko": "히바 → 우르겐치 ✈ 마드리드",
            "description_uz": "Urganch aeroportiga transfer. Toshkent orqali Madridga uchish. Dasturning yakuni.",
            "description_ru": "Трансфер в аэропорт Ургенча. Вылет через Ташкент в Мадрид. Окончание программы.",
            "description_en": "Transfer to Urgench airport. Flight to Madrid via Tashkent. End of program.",
            "description_ko": "우르겐치 공항 트랜스퍼. 타슈켄트 경유 마드리드행 비행. 프로그램 종료.",
        },
    ],

    # ── TAS-SKD 8 kun (yangi tour) ────────────────────────────────
    "classic-uzbekistan-tas-skd-8d": [
        {
            "day": 1, "title_uz": "Toshkentga uchish", "title_ru": "Вылет в Ташкент",
            "title_en": "Flight to Tashkent", "title_ko": "타슈켄트행 비행",
            "description_uz": "Yashash mamlakatidan Toshkentga uchish. Bortida tunash.",
            "description_ru": "Вылет из страны проживания в Ташкент. Ночь на борту.",
            "description_en": "Flight from home country to Tashkent. Overnight on board.",
            "description_ko": "거주국에서 타슈켄트행 비행. 기내 숙박.",
        },
        {
            "day": 2, "title_uz": "Toshkent", "title_ru": "Ташкент",
            "title_en": "Tashkent", "title_ko": "타슈켄트",
            "description_uz": "Aeroportda kutib olish, erta joylashish. Eski va zamonaviy Toshkent ekskursiyasi. Qo'shimcha: Usmon Qur'oni muzeyiga ekskursiya — 40 USD.",
            "description_ru": "Встреча в аэропорту, раннее заселение. Экскурсия по старому и современному Ташкенту. Доп: музей Корана Османа — 40 USD.",
            "description_en": "Airport meet, early check-in. Old & modern Tashkent tour. Optional: Quran of Uthman museum tour — $40.",
            "description_ko": "공항 미팅, 얼리 체크인. 구·현대 타슈켄트 투어. 선택: 우스만 쿠란 박물관 투어 — $40.",
        },
        {
            "day": 3, "title_uz": "Toshkent – Urganch – Xiva", "title_ru": "Ташкент – Ургенч – Хива",
            "title_en": "Tashkent – Urgench – Khiva", "title_ko": "타슈켄트 – 우르겐치 – 히바",
            "description_uz": "Urganchga parvoz va Xivaga o'tish. Ichan-Qal'a ekskursiyasi. Ixtiyoriy 'Happy Hour' — quyosh botishida vino — 10 USD.",
            "description_ru": "Перелёт в Ургенч и переезд в Хиву. Экскурсия по Ичан-Кале. Опция «Happy Hour» — вино на закате — 10 USD.",
            "description_en": "Flight to Urgench and drive to Khiva. Ichan-Kala tour. Optional 'Happy Hour' — wine at sunset — $10.",
            "description_ko": "우르겐치행 비행, 히바로 이동. 이찬칼라 투어. 선택 '해피아워' — 일몰의 와인 — $10.",
        },
        {
            "day": 4, "title_uz": "Xiva – Buxoro", "title_ru": "Хива – Бухара",
            "title_en": "Khiva – Bukhara", "title_ko": "히바 – 부하라",
            "description_uz": "Buxoroga o'tish (~450 km, 7-7,5 soat). Lunch box. Mehmonxonada joylashish.",
            "description_ru": "Переезд в Бухару (~450 км, 7-7,5 ч). Lunch box. Размещение.",
            "description_en": "Drive to Bukhara (~450 km, 7-7.5 hrs). Lunch box. Hotel check-in.",
            "description_ko": "부하라로 이동 (~450km, 7-7.5시간). 도시락. 호텔 체크인.",
        },
        {
            "day": 5, "title_uz": "Buxoro", "title_ru": "Бухара",
            "title_en": "Bukhara", "title_ko": "부하라",
            "description_uz": "Buxoro ekskursiyasi: Somoniylar, Chashma-Ayub, Bolo-Hovuz, Ark qal'asi, Labi-Hovuz, Ko'kaldosh, savdo gumbazlari, Po'i-Kalon.",
            "description_ru": "Экскурсия по Бухаре: Саманиды, Чашма-Аюб, Боло-Хауз, Арк, Ляби-Хауз, Кукельдаш, торговые купола, Пои-Калян.",
            "description_en": "Bukhara tour: Samanids, Chashma-Ayub, Bolo-Hauz, Ark, Lyab-i-Hauz, Kukeldash, trading domes, Poi-Kalyan.",
            "description_ko": "부하라 투어: 사마니드, 차슈마-아유브, 볼로하우즈, 아르크, 라비하우즈, 쿠켈다시, 무역 돔, 포이칼란.",
        },
        {
            "day": 6, "title_uz": "Buxoro – Samarqand", "title_ru": "Бухара – Самарканд",
            "title_en": "Bukhara – Samarkand", "title_ko": "부하라 – 사마르칸트",
            "description_uz": "Samarqandga o'tish. Ulug'bek rasadxonasi, Go'ri Amir maqbarasi, Registon maydoni. Kechqurun yoritilgan Registonga tashqi qarash.",
            "description_ru": "Переезд в Самарканд. Обсерватория Улугбека, мавзолей Гур-Эмир, площадь Регистан. Вечером — Регистан в подсветке.",
            "description_en": "Drive to Samarkand. Ulugh Beg observatory, Gur-e-Amir mausoleum, Registan Square. Evening — illuminated Registan.",
            "description_ko": "사마르칸트로 이동. 울루그벡 천문대, 구르 에미르 영묘, 레기스탄 광장. 저녁 — 조명 켜진 레기스탄.",
        },
        {
            "day": 7, "title_uz": "Samarqand", "title_ru": "Самарканд",
            "title_en": "Samarkand", "title_ko": "사마르칸트",
            "description_uz": "'Meros' qog'oz fabrikasi, Shohi-Zinda, Bibi-Xonim masjidi, Siyob bozori. Ekskursiya 15:00 gacha.",
            "description_ru": "Фабрика бумаги «Мерос», Шахи-Зинда, мечеть Биби-Ханым, базар Сиаб. Экскурсия до 15:00.",
            "description_en": "Meros paper factory, Shah-i-Zinda, Bibi-Khanym mosque, Siab bazaar. Tour until 15:00.",
            "description_ko": "메로스 종이 공장, 샤히진다, 비비하늠 모스크, 시압 시장. 15:00까지 투어.",
        },
        {
            "day": 8, "title_uz": "Samarqand → Uchish", "title_ru": "Самарканд → Вылет",
            "title_en": "Samarkand → Departure", "title_ko": "사마르칸트 → 출발",
            "description_uz": "Samarqand aeroportiga transfer va xizmat ko'rsatishning yakuni.",
            "description_ru": "Трансфер в аэропорт Самарканда и завершение обслуживания.",
            "description_en": "Transfer to Samarkand airport and end of services.",
            "description_ko": "사마르칸트 공항 트랜스퍼와 서비스 종료.",
        },
    ],
}


class Command(BaseCommand):
    help = "Qo'shimcha tour (TAS-SKD) va qolgan itinerary'larni DBga yozadi"

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            Tour = apps.get_model('tours', 'Tour')
            Region = apps.get_model('regions', 'Region')
        except LookupError as e:
            self.stderr.write(self.style.ERROR(f"Model topilmadi: {e}"))
            return

        Category = None
        for app_label in ['tours', 'categories']:
            try:
                Category = apps.get_model(app_label, 'Category')
                break
            except LookupError:
                continue

        # Itinerary model
        ItineraryDay = None
        for model_name in ['ItineraryDay', 'TourDay', 'TourItinerary', 'Day']:
            try:
                ItineraryDay = apps.get_model('tours', model_name)
                break
            except LookupError:
                continue

        # ── 1. YANGI TOUR (TAS-SKD) ─────────────────────────────
        self.stdout.write(self.style.NOTICE("\n🧳 Yangi tour qo'shish (TAS-SKD)..."))

        tour_fields = {f.name for f in Tour._meta.get_fields()}
        defaults = {}
        for key, val in EXTRA_TOUR.items():
            if key in ('slug', 'region_slug', 'category_slug', 'image_url'):
                continue
            if key.startswith('included_') or key.startswith('excluded_'):
                continue
            if key in tour_fields:
                defaults[key] = val

        # title moslamasi
        if 'title' in tour_fields and 'name' not in tour_fields:
            defaults['title'] = EXTRA_TOUR['name_uz']
            for lang in ['uz', 'ru', 'en', 'ko']:
                if f'title_{lang}' in tour_fields:
                    defaults[f'title_{lang}'] = EXTRA_TOUR.get(f'name_{lang}', '')
            for k in list(defaults.keys()):
                if k.startswith('name'):
                    defaults.pop(k, None)

        # Region va kategoriya
        try:
            region = Region.objects.get(slug=EXTRA_TOUR['region_slug'])
            if 'region' in tour_fields:
                defaults['region'] = region
        except Region.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"  ✗ Region topilmadi: {EXTRA_TOUR['region_slug']}"))

        if Category and 'category' in tour_fields:
            try:
                cat = Category.objects.get(slug=EXTRA_TOUR['category_slug'])
                defaults['category'] = cat
            except Category.DoesNotExist:
                pass

        obj, created = Tour.objects.update_or_create(slug=EXTRA_TOUR['slug'], defaults=defaults)
        mark = "✓ yaratildi" if created else "↺ yangilandi"
        self.stdout.write(f"  {mark}  ${EXTRA_TOUR['price']}  {EXTRA_TOUR['name_uz']}")

        # ── 2. ITINERARIES ──────────────────────────────────────
        if not ItineraryDay:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  ItineraryDay modeli topilmadi — itinerary'lar qo'shilmadi.\n"
                "Iltimos, tours/models.py da quyidagi modelni qo'shing va migration qiling:\n\n"
                "class ItineraryDay(models.Model):\n"
                "    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary')\n"
                "    day = models.PositiveIntegerField()\n"
                "    title = models.CharField(max_length=200)\n"
                "    description = models.TextField()\n"
                "    class Meta:\n"
                "        ordering = ['day']"
            ))
            return

        self.stdout.write(self.style.NOTICE("\n📅 Itinerary'larni qo'shish..."))
        itinerary_fields = {f.name for f in ItineraryDay._meta.get_fields()}

        for tour_slug, days in EXTRA_ITINERARIES.items():
            try:
                tour = Tour.objects.get(slug=tour_slug)
            except Tour.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ✗ Tour topilmadi: {tour_slug}"))
                continue

            ItineraryDay.objects.filter(tour=tour).delete()

            for d in days:
                day_defaults = {}
                for key, val in d.items():
                    if key == 'day':
                        day_defaults['day'] = val
                    elif key in itinerary_fields:
                        day_defaults[key] = val
                if 'title' in itinerary_fields and 'title' not in day_defaults:
                    day_defaults['title'] = d.get('title_uz', '')
                if 'description' in itinerary_fields and 'description' not in day_defaults:
                    day_defaults['description'] = d.get('description_uz', '')

                ItineraryDay.objects.create(tour=tour, **day_defaults)

            self.stdout.write(f"  ✓ {tour_slug:42s}  {len(days)} kun")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ TAYYOR! 1 yangi tour qo'shildi, {len(EXTRA_ITINERARIES)} tour uchun itinerary yozildi.\n"
            f"   Saytda ko'rish: http://localhost:8008/uz/tours/\n"
        ))