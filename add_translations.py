# Tarjimalar
translations = {
    "Get exclusive offers and Silk Road travel inspiration.": "Maxsus takliflar va Ipak yo'li sayohati ilhomini oling.",
    "Our support team is available 24/7 to assist with your booking.": "Qo'llab-quvvatlash jamoasi bronlashda yordam berish uchun 24/7 mavjud.",
    "Luxury Silk Road Travel": "Hashamatli Ipak yo'li sayohati",
    "Hero": "Hero",
    "Uzbekistan · Silk Road · Beyond": "O'zbekiston · Ipak yo'li · undan tashqari",
    "Where Ancient Routes": "Qadimiy yo'llar",
    "Become Your Story": "Sizing hikoyangizga aylanadi",
    "Where to?": "Qayerga?",
    "Recent searches": "So'nggi qidiruvlar",
    "Desert": "Cho'l",
    "Age 12 or above": "12 yosh va undan katta",
    "Reset": "Tiklash",
    "Done": "Tayyor",
    "Hotel booking coming soon": "Mehmonxona bronlash tez orada",
    "We're partnering with the best hotels. Stay tuned!": "Biz eng yaxshi mehmonxonalar bilan hamkorlik qilamiz. Kuzatib boring!",
    "Tickets coming soon": "Chiptalar tez orada",
    "Train and air tickets will be available soon.": "Poyezd va aviachiptalar tez orada mavjud bo'ladi.",
    "Car rental coming soon": "Mashina ijarasi tez orada",
    "Explore on your own terms — coming soon!": "O'z sharoitingizda kashf eting — tez orada!",
    "Culinary": "Ovqatlanish",
    "Wellness": "Salomatlik",
    "Anywhere": "Har qayerda",
    "Discover the jewels of the ancient Silk Road": "Qadimiy Ipak yo'li durdonalarini kashf eting",
    "Every detail crafted so you focus on the moments that matter.": "Har bir tafsilot siz muhim daqiqalarga e'tibor qaratishingiz uchun yaratilgan.",
    "Our local team is always ready to help.": "Mahalliy jamoamiz har doim yordam berishga tayyor.",
    "No Hidden Fees": "Yashirin to'lovlar yo'q",
    "Expert Guides": "Malakali gidlar",
    "Certified local guides with deep Silk Road knowledge.": "Ipak yo'li bo'yicha chuqur bilimga ega sertifikatlangan mahalliy gidlar.",
    "Tailored Routes": "Moslashtirilgan marshrutlar",
    "Itineraries shaped around how you love to travel.": "Sayohat qilishni yoqtirishingizga qarab shakllantirilgan dasturlar.",
    "Browse by style": "Uslub bo'yicha ko'rish",
    "Find your perfect travel experience": "Mukammal sayohat tajribangizni toping",
    "Stay Ahead of Every Adventure": "Har bir sayohatdan oldinda boring",
    "Join 2,400+ travelers. Unsubscribe anytime.": "2400+ sayohatchiga qo'shiling. Istalgan vaqtda obunani bekor qiling.",
    "Thank you for reaching out. Oygul will get back to you within 24 hours.": "Murojaat qilganingiz uchun rahmat. Oygul 24 soat ichida siz bilan bog'lanadi.",
    "Choose your payment method. All payments are in Uzbek Som (UZS).": "To'lov usulingizni tanlang. Barcha to'lovlar O'zbek so'mida (UZS).",
    "Must-see places": "Ko'rinishi shart bo'lgan joylar",
    "Top Attractions": "Eng yaxshi diqqatga sazor joylar",
    "Discover": "Kashf eting",
    "Years of history": "Yillik tarix",
    "UNESCO sites": "UNESCO ob'ektlari",
    "Scroll to explore": "Kashf etish uchun aylantiring",
    "regions": "viloyatlar",
    "UNESCO Heritage": "UNESCO merosi",
    "4 world heritage sites across the country": "Mamlakat bo'ylab 4 ta jahon merosi ob'ekti",
    "Safe Travel": "Xavfsiz sayohat",
    "Consistently rated one of the safest destinations in Asia": "Doimiy ravishda Osiyodagi eng xavfsiz manzillardan biri deb baholanadi",
    "Rich Cuisine": "Boy oshxona",
    "Plov, samsa, shashlik — unforgettable flavors": "Palov, somsa, shashlik — unutilmas ta'mlar",
}

# Tarjima faylini o'qish
with open('/app/locale/uz/LC_MESSAGES/django.po', 'r') as f:
    content = f.read()

# Tarjimalarni qo'shish
for msgid, msgstr in translations.items():
    # Agar mavjud bo'lsa, yangilash
    old = f'msgid "{msgid}"\nmsgstr ""'
    new = f'msgid "{msgid}"\nmsgstr "{msgstr}"'
    if old in content:
        content = content.replace(old, new)

# Faylni saqlash
with open('/app/locale/uz/LC_MESSAGES/django.po', 'w') as f:
    f.write(content)

print(f'{len(translations)} ta tarjima qo\'shildi/yangilandi')
