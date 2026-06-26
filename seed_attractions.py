import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from regions.models import Region, Attraction

# Regionlarni olish
toshkent = Region.objects.get(slug='toshkent')
samarqand = Region.objects.get(slug='samarqand')
buxoro = Region.objects.get(slug='buxoro')
xiva = Region.objects.get(slug='xiva')
fargona = Region.objects.get(slug='fargona')

attractions_data = {
    toshkent: [
        {'name_uz': 'Hazrati Imom majmuasi', 'name_ru': 'Комплекс Хаст-Имам', 'name_en': 'Hast-Imam Complex', 'description_uz': 'Toshkentning eng qadimiy diniy markazi. XV-XVI asrlarda qurilgan.', 'description_ru': 'Древнейший религиозный центр Ташкента. Построен в XV-XVI веках.', 'description_en': 'Ancient religious center of Tashkent. Built in 15th-16th centuries.', 'latitude': 41.3049, 'longitude': 69.2789, 'order': 1},
        {'name_uz': 'Chorsu bozori', 'name_ru': 'Базар Чорсу', 'name_en': 'Chorsu Bazaar', 'description_uz': 'Toshkentning eng katta va qadimiy bozori. Yuzlab yillar tarixiga ega.', 'description_ru': 'Крупнейший и древнейший базар Ташкента. Имеет вековую историю.', 'description_en': 'Largest and oldest bazaar of Tashkent. Has centuries of history.', 'latitude': 41.3055, 'longitude': 69.2778, 'order': 2},
        {'name_uz': 'Barak-xana madrasasi', 'name_ru': 'Медресе Барак-хана', 'name_en': 'Barak-Khan Madrasah', 'description_uz': 'XVI asrda qurilgan tarixiy madrasa. Hozirda islom instituti sifatida ishlaydi.', 'description_ru': 'Историческая медресе XVI века. Сейчас работает как исламский институт.', 'description_en': 'Historical madrasah from 16th century. Now operates as Islamic institute.', 'latitude': 41.3048, 'longitude': 69.2787, 'order': 3},
        {'name_uz': 'Toshkent teleminorasi', 'name_ru': 'Телебашня Ташкента', 'name_en': 'Tashkent TV Tower', 'description_uz': '375 metr balandlikdagi teleminorasi. Toshkentning eng baland binosi.', 'description_ru': 'Телевышка высотой 375 метров. Самое высокое здание Ташкента.', 'description_en': 'TV tower 375 meters high. Tallest building in Tashkent.', 'latitude': 41.3183, 'longitude': 69.2786, 'order': 4},
        {'name_uz': 'Amir Temur xiyoboni', 'name_ru': 'Парк Амира Тимура', 'name_en': 'Amir Timur Park', 'description_uz': 'Toshkentning markaziy bog\'i. Buyuk Amir Temur haykali joylashgan.', 'description_ru': 'Центральный парк Ташкента. Здесь расположен памятнику Амиру Тимуру.', 'description_en': 'Central park of Tashkent. Monument to Amir Timur is located here.', 'latitude': 41.3111, 'longitude': 69.2797, 'order': 5},
        {'name_uz': 'Toshkent metrosi', 'name_ru': 'Метрополитен Ташкента', 'name_en': 'Tashkent Metro', 'description_uz': 'Markaziy Osiyodagi birinchi metro. Chiroyli bekatlar bilan mashhur.', 'description_ru': 'Первое метро в Центральной Азии. Известно красивыми станциями.', 'description_en': 'First metro in Central Asia. Famous for beautiful stations.', 'latitude': 41.3000, 'longitude': 69.2800, 'order': 6},
    ],
    samarqand: [
        {'name_uz': 'Registon maydoni', 'name_ru': 'Площадь Регистан', 'name_en': 'Registan Square', 'description_uz': 'Dunyodagi eng go\'zal me\'moriy majmalaridan biri. Uchta madrasadan iborat.', 'description_ru': 'Один из самых красивых архитектурных ансамблей мира. Состоит из трёх медресе.', 'description_en': 'One of the most beautiful architectural ensembles in the world. Consists of three madrasahs.', 'latitude': 39.6542, 'longitude': 66.9756, 'order': 1},
        {'name_uz': 'Gur-Emir maqbarasi', 'name_ru': 'Мавзолей Гур-Эмир', 'name_en': 'Gur-Emir Mausoleum', 'description_uz': 'Amir Temur va uning avlodlari dafn etilgan joy. Yaltirroq gumbazi bilan tanilgan.', 'description_ru': 'Место захоронения Амира Тимура и его потомков. Известен сверкающим куполом.', 'description_en': 'Burial place of Amir Timur and his descendants. Known for its sparkling dome.', 'latitude': 39.6485, 'longitude': 66.9794, 'order': 2},
        {'name_uz': 'Shohizinda', 'name_ru': 'Шахи-Зинда', 'name_en': 'Shah-i-Zinda', 'description_uz': '14 km uzunlikdagi ko\'cha. Yuzlab tarixiy qabrlar va maqbaralar joylashgan.', 'description_ru': 'Улица протяжённостью 14 км. Здесь расположены сотни исторических могил и мавзолеев.', 'description_en': 'Street stretching 14 km. Hundreds of historical graves and mausoleums are located here.', 'latitude': 39.6567, 'longitude': 66.9848, 'order': 3},
        {'name_uz': 'Ulug\'bek rasadxonasi', 'name_ru': 'Обсерватория Улугбека', 'name_en': 'Ulugh Beg Observatory', 'description_uz': 'XV asrda qurilgan rasadxona. Buyuk olim Ulug\'bek ishlagan joy.', 'description_ru': 'Обсерватория XV века. Здесь работал великий учёный Улугбек.', 'description_en': 'Observatory from 15th century. Great scientist Ulugh Beg worked here.', 'latitude': 39.6610, 'longitude': 66.9910, 'order': 4},
        {'name_uz': 'Bibi-Xonim masjidi', 'name_ru': 'Мечеть Биби-Ханым', 'name_en': 'Bibi-Khanym Mosque', 'description_uz': 'Samarqanddagi eng katta masjid. XV asrda Amir Temur tomonidan qurilgan.', 'description_ru': 'Крупнейшая мечеть Самарканда. Построена Амиром Тимуром в XV веке.', 'description_en': 'Largest mosque in Samarkand. Built by Amir Timur in 15th century.', 'latitude': 39.6533, 'longitude': 66.9794, 'order': 5},
        {'name_uz': 'Siyob bozori', 'name_ru': 'Базар Сиаб', 'name_en': 'Siab Bazaar', 'description_uz': 'Samarqanddagi eng katta bozor. Mevalar va ziravorlar bilan mashhur.', 'description_ru': 'Крупнейший базар Самарканда. Известен фруктами и специями.', 'description_en': 'Largest bazaar in Samarkand. Famous for fruits and spices.', 'latitude': 39.6520, 'longitude': 66.9810, 'order': 6},
    ],
    buxoro: [
        {'name_uz': 'Po-i-Kalyan majmuasi', 'name_ru': 'Ансамбль Пои-Калян', 'name_en': 'Po-i-Kalyan Ensemble', 'description_uz': 'Buxoroning eng baland minorasi va ikkita madrasadan iborat majmalar.', 'description_ru': 'Ансамбль из самой высокой минарета Бухары и двух медресе.', 'description_en': 'Ensemble of the tallest minaret in Bukhara and two madrasahs.', 'latitude': 39.7767, 'longitude': 64.4208, 'order': 1},
        {'name_uz': 'Ark qal\'asi', 'name_ru': 'Крепость Арк', 'name_en': 'Ark Fortress', 'description_uz': 'Buxoroning eng qadimiy qal\'asi. 2000 yildan ortiq tarixga ega.', 'description_ru': 'Древнейшая крепость Бухары. Имеет более 2000 лет истории.', 'description_en': 'Ancient fortress of Bukhara. Has over 2000 years of history.', 'latitude': 39.7758, 'longitude': 64.4197, 'order': 2},
        {'name_uz': 'Somoniyalar maqbarasi', 'name_ru': 'Мавзолей Саманидов', 'name_en': 'Samanid Mausoleum', 'description_uz': 'IX-X asrda qurilgan. Buxoroning eng qadimiy binosi.', 'description_ru': 'Построен в IX-X веках. Древнейшее сооружение Бухары.', 'description_en': 'Built in 9th-10th centuries. Oldest structure in Bukhara.', 'latitude': 39.7789, 'longitude': 64.4217, 'order': 3},
        {'name_uz': 'Bolo-Hovuz masjidi', 'name_ru': 'Мечеть Боло-Хауз', 'name_en': 'Bolo-Khauz Mosque', 'description_uz': 'XVIII asrda qurilgan chiroyli masjid. Oyna ustunlari bilan tanilgan.', 'description_ru': 'Красивая мечеть XVIII века. Известна зеркальными колоннами.', 'description_en': 'Beautiful mosque from 18th century. Known for mirror columns.', 'latitude': 39.7760, 'longitude': 64.4205, 'order': 4},
        {'name_uz': 'Chashma Ayub', 'name_ru': 'Чашма-Аюб', 'name_en': 'Chashma-Ayub', 'description_uz': 'Muqaddas suv manbai. Payg\'ambar Ayub (Yov) bilan bog\'liq.', 'description_ru': 'Священный источник воды. Связан с пророком Айюбом (Иовом).', 'description_en': 'Sacred water source. Associated with Prophet Ayub (Job).', 'latitude': 39.7775, 'longitude': 64.4210, 'order': 5},
        {'name_uz': 'Ticorat gumbazlari', 'name_ru': 'Торговые купола', 'name_en': 'Trading Domes', 'description_uz': 'XVI asrdagi ticorat gumbazlari. Ziravorlar, ipak va boshqa mahsulotlar sotilgan.', 'description_ru': 'Торговые купола XVI века. Здесь продавались специи, шёлк и другие товары.', 'description_en': 'Trading domes from 16th century. Spices, silk and other goods were sold here.', 'latitude': 39.7762, 'longitude': 64.4200, 'order': 6},
    ],
    xiva: [
        {'name_uz': 'Ichan-Qala', 'name_ru': 'Ичан-Кала', 'name_en': 'Ichan-Kala', 'description_uz': 'Xivaning ichki shahri. ЮНЕСKO merosi ro\'yxatiga kiritilgan.', 'description_ru': 'Внутренний город Хивы. Включён в список объектов ЮНЕСКО.', 'description_en': 'Inner city of Khiva. Included in UNESCO World Heritage list.', 'latitude': 41.3786, 'longitude': 60.3564, 'order': 1},
        {'name_uz': 'Kalta-Minor minoretasi', 'name_ru': 'Минарет Кальта-Минор', 'name_en': 'Kalta-Minor Minaret', 'description_uz': 'Xivaning eng baland minorasi. 26 metr balandlikda.', 'description_ru': 'Самая высокая минарета Хивы. Высотой 26 метров.', 'description_en': 'Tallest minaret in Khiva. 26 meters high.', 'latitude': 41.3789, 'longitude': 60.3560, 'order': 2},
        {'name_uz': 'Kunya-Ark qal\'asi', 'name_ru': 'Крепость Куня-Арк', 'name_en': 'Kunya-Ark Fortress', 'description_uz': 'Xivaning qadimiy qal\'asi. XVII asrda qayta qurilgan.', 'description_ru': 'Древняя крепость Хивы. Перестроена в XVII веке.', 'description_en': 'Ancient fortress of Khiva. Rebuilt in 17th century.', 'latitude': 41.3790, 'longitude': 60.3558, 'order': 3},
        {'name_uz': 'Juma masjidi', 'name_ru': 'Мечеть Джума', 'name_en': 'Juma Mosque', 'description_uz': 'XII asrda qurilgan. 218 ta yog\'och ustun bilan tanilgan.', 'description_ru': 'Построена в XII веке. Известна 218 деревянными колоннами.', 'description_en': 'Built in 12th century. Known for 218 wooden columns.', 'latitude': 41.3785, 'longitude': 60.3565, 'order': 4},
        {'name_uz': 'Tosh-Xovli saroyi', 'name_ru': 'Дворец Таш-Ховли', 'name_en': 'Tash-Khovli Palace', 'description_uz': 'XIX asrda qurilgan hokimlar saroyi. Chiroyli g\'isht naqshlari bilan bezatilgan.', 'description_ru': 'Дворец ханов XIX века. Украшен красивыми кирпичными узорами.', 'description_en': 'Khans palace from 19th century. Decorated with beautiful brick patterns.', 'latitude': 41.3787, 'longitude': 60.3562, 'order': 5},
        {'name_uz': 'Islom-Xodji minoretasi', 'name_ru': 'Минарет Ислам-Ходжи', 'name_en': 'Islam-Khoja Minaret', 'description_uz': 'Xivaning eng baland minorasi. 57 metr balandlikda.', 'description_ru': 'Самая высокая минарета Хивы. Высотой 57 метров.', 'description_en': 'Tallest minaret in Khiva. 57 meters high.', 'latitude': 41.3788, 'longitude': 60.3563, 'order': 6},
    ],
    fargona: [
        {'name_uz': 'Marg\'ilon ipak fabrikasi', 'name_ru': 'Шёлковая фабрика Маргилана', 'name_en': 'Margilan Silk Factory', 'description_uz': 'O\'zbekistonning eng katta ipak ishlab chiqaruvchisi. An\'anaviy usulda.', 'description_ru': 'Крупнейший производитель шёлка в Узбекистане. Традиционным способом.', 'description_en': 'Largest silk producer in Uzbekistan. Traditional methods.', 'latitude': 40.4725, 'longitude': 71.7242, 'order': 1},
        {'name_uz': 'Farg\'ona vodiyi tabiati', 'name_ru': 'Природа Ферганской долины', 'name_en': 'Fergana Valley Nature', 'description_uz': 'O\'zbekistonning eng go\'zal tabiat manzillaridan biri.', 'description_ru': 'Одно из самых красивых природных мест Узбекистана.', 'description_en': 'One of the most beautiful natural places in Uzbekistan.', 'latitude': 40.3800, 'longitude': 71.7800, 'order': 2},
        {'name_uz': 'Rishton kashtachilik', 'name_ru': 'Керамика Риштана', 'name_en': 'Rishton Ceramics', 'description_uz': 'O\'zbekistonning eng qadimiy kashtachilik markazi. An\'anaviy ko\'k rang.', 'description_ru': 'Древнейший центр керамики Узбекистана. Традиционный голубой цвет.', 'description_en': 'Ancient ceramics center of Uzbekistan. Traditional blue color.', 'latitude': 40.3550, 'longitude': 71.2850, 'order': 3},
        {'name_uz': 'Kokand hokimlik saroyi', 'name_ru': 'Дворец Худояр-хана', 'name_en': 'Khudoyar-Khan Palace', 'description_uz': 'XIX asrda qurilgan Kokand hokimlarining saroyi.', 'description_ru': 'Дворец правителей Коканда XIX века.', 'description_en': 'Palace of Kokand rulers from 19th century.', 'latitude': 40.5283, 'longitude': 70.9425, 'order': 4},
        {'name_uz': 'Shohimardon chashmasi', 'name_ru': 'Источник Шахимардан', 'name_en': 'Shahimardon Spring', 'description_uz': 'Muqaddas suv manbai. Ziyoratchilar uchun mashhur joy.', 'description_ru': 'Священный источник. Популярное место для паломников.', 'description_en': 'Sacred spring. Popular place for pilgrims.', 'latitude': 40.2000, 'longitude': 71.5000, 'order': 5},
        {'name_uz': 'Andijon tarixiy muzeyi', 'name_ru': 'Андижанский исторический музей', 'name_en': 'Andijan Historical Museum', 'description_uz': 'Andijon viloyatining tarixini saqlab qo\'ygan muzey.', 'description_ru': 'Музей, хранящий историю Андижанской области.', 'description_en': 'Museum preserving the history of Andijan region.', 'latitude': 40.7821, 'longitude': 72.3442, 'order': 6},
    ],
}

for region, attractions in attractions_data.items():
    for ad in attractions:
        a, created = Attraction.objects.get_or_create(
            region=region,
            name_uz=ad['name_uz'],
            defaults=ad
        )
        if created:
            print(f'  + {ad["name_uz"]} ({region.name_uz})')
        else:
            print(f'  = {ad["name_uz"]} already exists')

print()
print(f'Total attractions: {Attraction.objects.count()}')
for r in Region.objects.all():
    count = r.attractions.count()
    print(f'  {r.name_uz}: {count} attractions')
