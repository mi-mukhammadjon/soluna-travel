# Qo'shimcha tarjimalar
translations = {
    "Warm Hospitality": "Issiq mezmondo'stlik",
    "Famously welcoming locals and vibrant culture": "Mashhur mezmondo'st mahalliy aholi va boy madaniyat",
    "Can't decide where to go?": "Qayerga borishni bilmayapsizmi?",
    "Talk to an expert": "Mutaxassis bilan gaplashing",
    "Back": "Orqaga",
    "Click to rate": "Baholash uchun bosing",
    "Title": "Sarlavha",
    "Tell others about your experience — what did you enjoy most?": "Boshqalarga o'z tajribangiz haqida ayting — eng ko'p nima yoqdi?",
    "Minimum 10 characters": "Kamida 10 ta belgi",
    "Poor — not recommended": "Yomon — tavsiya etilmaydi",
    "Average — decent experience": "O'rtacha — yaxshi tajriba",
    "Good — would recommend": "Yaxshi — tavsiya qilaman",
    "Excellent — outstanding experience!": "Ajoyib — ajoyib tajriba!",
    "and consent to receive travel inspiration emails": "va sayohat ilhomini olish uchun email rozilik",
    "Save to wishlist": "Sevimlilar ro'yxatiga saqlash",
    "from": "dan",
    "Difficulty": "Qiyinchilik",
    "Awaiting approval": "Tasdiqlash kutilmoqda",
    "No reviews yet. Be the first to share your experience!": "Hali sharhlar yo'q. Birinchi bo'lib tajribangizni ulashing!",
    "Talk to a travel expert": "Sayohat mutaxassisi bilan gaplashing",
    "Get free advice": "Bepul maslahat oling",
    "Link copied!": "Havola nusxalandi!",
    "Added to wishlist": "Sevimlilar ro'yxatiga qo'shildi",
    "Removed from wishlist": "Sevimlilar ro'yxatidan o'chirildi",
    "Extraordinary": "Ajoyib",
    "handcrafted journeys through Uzbekistan": "O'zbekiston bo'ylab qo'lda yaratilgan sayohatlar",
    "Error loading tours": "Turlarni yuklashda xatolik",
}

# Tarjima faylini o'qish
with open('/app/locale/uz/LC_MESSAGES/django.po', 'r') as f:
    content = f.read()

# Tarjimalarni qo'shish
added = 0
for msgid, msgstr in translations.items():
    old = f'msgid "{msgid}"\nmsgstr ""'
    new = f'msgid "{msgid}"\nmsgstr "{msgstr}"'
    if old in content:
        content = content.replace(old, new)
        added += 1

# Faylni saqlash
with open('/app/locale/uz/LC_MESSAGES/django.po', 'w') as f:
    f.write(content)

print(f'{added} ta tarjima qo\'shildi/yangilandi')
