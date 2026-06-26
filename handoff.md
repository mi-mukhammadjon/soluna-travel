# SoLuna Touroperator — Project Handoff

**Loyiha:** SoLuna — O'zbekiston bo'yicha premium tur agentlik web sayti  
**Brend:** SoLuna (solunatravel.uz)  
**Egasi:** Oygul Axatova — Touroperator  
**Stack:** Django 4.2 + PostgreSQL 15 + Redis 7 + Celery 5.3 + Docker  
**Sana:** Iyun 2025

---

## 1. Arxitektura

```
soluna/
├── config/                  # Django sozlamalari, URL lar, Celery
│   ├── settings.py          # Asosiy settings (300+ qator)
│   ├── settings_build.py    # Build vaqtida minimal settings (SQLite)
│   ├── urls.py              # Asosiy URL router (i18n_patterns bilan)
│   ├── celery.py            # Celery app konfiguratsiyasi
│   ├── admin.py             # Custom SoLunaAdminSite
│   ├── admin_dashboard.py   # Admin dashboard API (KPI, recent items)
│   ├── wsgi.py              # WSGI entry point
│   └── asgi.py              # ASGI entry point (uvicorn uchun)
│
├── accounts/                # Foydalanuvchi tizimi
│   ├── models.py            # Custom User model
│   ├── views.py             # Profil, registratsiya, parol o'zgartirish
│   ├── urls.py              # Profil URL lari
│   ├── forms.py             # ProfileUpdateForm
│   ├── admin.py             # Custom UserAdmin
│   ├── signals.py           # Allauth signup signali -> welcome email
│   ├── tasks.py             # Celery: send_welcome_email
│   └── apps.py              # AppConfig + signals ready()
│
├── regions/                 # Viloyatlar va attraksiyalar
│   ├── models.py            # Region, Attraction
│   ├── views.py             # ListView, DetailView
│   ├── urls.py              # Region URL lari
│   ├── translation.py       # modeltranslation: name, description
│   └── admin.py
│
├── tours/                   # Turlar, kategoriyalar, galereya
│   ├── models.py            # Tour, TourCategory, TourImage, ItineraryDay,
│   │                        #   CompanyStatistic, CompanyAdvantage
│   ├── views.py             # HomeView, TourListView, TourDetailView, 404/500
│   ├── urls.py              # Tour URL lari
│   ├── urls_home.py         # Bosh sahifa URL
│   ├── translation.py       # modeltranslation: title, description, ...
│   ├── templatetags/
│   │   └── lang_tags.py     # Til kodidan native nom filteri
│   └── management/commands/ # Seed komandalari
│       ├── seed_real_tours.py
│       ├── seed_extra_tours.py
│       ├── seed_tour_itineraries.py
│       └── populate_tours.py
│
├── bookings/                # Bronlar tizimi
│   ├── models.py            # Booking (pending->confirmed->completed/cancelled)
│   ├── views.py             # CRUD bronlar uchun
│   ├── urls.py              # Bron URL lari
│   ├── forms.py             # BookingForm
│   ├── tasks.py             # Celery: tasdiqlash/bekor qilish email
│   └── admin.py
│
├── payments/                # To'lov tizimi (Click + Payme)
│   ├── models.py            # Payment, Currency (valyuta konversiya)
│   ├── views.py             # To'lov sahifalari, webhook lar, mock mode
│   ├── urls.py              # To'lov URL lari
│   ├── gateways/
│   │   ├── click.py         # Click.uz SHOP API (Prepare + Complete)
│   │   └── payme.py         # Payme Merchant API (JSON-RPC 2.0)
│   └── management/commands/
│       └── seed_currencies.py
│
├── messages_app/            # Contact form va email/SMS javob
│   ├── models.py            # ContactMessage
│   ├── views.py             # ContactView, MessageReplyView
│   ├── urls.py
│   ├── forms.py             # ContactForm, ReplyForm
│   ├── tasks.py             # Celery: admin xabarnoma, javob email, SMS
│   └── admin.py
│
├── reviews/                 # Reyting va izohlar
│   ├── models.py            # Review (1-5 yulduz, user+tour unique)
│   ├── views.py             # CRUD reviewlar
│   ├── urls.py
│   ├── forms.py             # ReviewForm
│   └── admin.py
│
├── places/                  # 2GIS yaqin joylar API
│   ├── models.py            # NearbyPlace (cafe, hotel, museum, ...)
│   ├── views.py             # NearbyPlacesAPIView, AttractionNearbyView
│   ├── urls.py
│   └── dgis.py              # 2GIS API wrapper
│
├── templates/               # HTML templatelar (54+ fayl)
│   ├── admin/               # Custom admin panel (Karvon teması)
│   ├── account/             # Allauth autentifikatsiya
│   ├── accounts/            # Custom profil sahifalari
│   ├── tours/               # List, detail
│   ├── regions/             # List, detail
│   ├── bookings/            # List, detail, create
│   ├── payments/            # To'lov sahifalari
│   ├── messages_app/        # Contact form
│   ├── reviews/             # Sharh yozish
│   ├── socialaccount/       # Ijtimoiy kirish
│   └── partials/            # Til almashtirgich
│
├── static/
│   ├── css/
│   │   ├── main.css         # Asosiy CSS (barcha sahifalar)
│   │   ├── soluna-premium.css # Premium dizayn tizimi
│   │   ├── home-magazine.css  # Bosh sahifa
│   │   ├── add.css          # Qo'shimcha stillar
│   │   └── admin.css        # Admin panel (Karvon teması)
│   ├── js/
│   │   └── main.js          # Scroll reveal, counter, theme toggle
│   ├── img/
│   │   ├── hero.jpg
│   │   └── logos/
│   └── assets/flags/        # Til bayroqlari
│
├── locale/                  # Tarjima fayllari (10 til)
├── media/                   # Yuklangan fayllar
├── staticfiles/             # collectstatic natijasi
├── logs/                    # Log fayllar
├── backups/                 # SQL zaxiralar
│
├── Dockerfile               # Ubuntu 22.04 + Python 3.11
├── docker-compose.yml       # 5 servis: web, db, redis, celery, celery_beat
├── entrypoint.sh            # DB/Redis kutish, migrate, collectstatic
├── start.sh                 # CRLF tozalab entrypoint ni ishga tushirish
├── deploy.sh                # Git pull, build, migrate, collectstatic
├── backup.sh                # PostgreSQL dump (7 kun saqlash)
├── requirements.txt         # Python kutubxonalari
├── .env                     # Muhit o'zgaruvchilari
└── handoff.md               # Loyiha hujjati (siz o'qiyotgan fayl)
```

---

## 2. Docker Servislar

| Servis | Image | Port | Vazifa |
|--------|-------|------|--------|
| **web** | Ubuntu 22.04 + Python 3.11 | 8008 | Django server (dev: runserver, prod: uvicorn/gunicorn) |
| **db** | postgres:15-alpine | 5432 | PostgreSQL ma'lumotlar bazasi |
| **redis** | redis:7-alpine | 6379 | Cache + Celery broker |
| **celery** | Ubuntu 22.04 + Python 3.11 | — | Async tasklar (email, SMS) |
| **celery_beat** | Ubuntu 22.04 + Python 3.11 | — | Periodic tasks scheduler |

### Dockerfile xususiyatlari:
- Asos: **Ubuntu 22.04** (python:3.11-slim emas!)
- Deadsnakes PPA orqali Python 3.11 o'rnatiladi
- System kutubxonalar: build-essential, libjpeg, libpq, libffi, libssl, gettext
- CRLF tozalash: `dos2unix`
- Port: **8008**

### entrypoint.sh jarayoni:
1. PostgreSQL kutish (30 ta urinish, har 2 soniyada)
2. Redis kutish (15 ta urinish)
3. `migrate --noinput`
4. `compilemessages` (uz, ru, ko, en)
5. `collectstatic --noinput`
6. Superuser yaratish (agar `DJANGO_SUPERUSER_EMAIL` bor bo'lsa)
7. Production: uvicorn yoki gunicorn (4 worker)
8. Dev: `runserver 0.0.0.0:8008`

### Volumelar:
- `postgres_data` — PostgreSQL ma'lumotlari
- `redis_data` — Redis ma'lumotlari
- `staticfiles` — Static fayllar
- `media` — Yuklangan fayllar

### Ishga tushirish:
```bash
# .env faylni to'ldiring
cp .env.example .env

# Build va ishga tushirish
docker compose up -d --build

# Holat
docker compose ps
docker compose logs -f web
```

---

## 3. .env O'zgaruvchilar

```env
# Django
SECRET_KEY=django-insecure-...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=tour_agency
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379

# Email (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=SoLuna <noreply@solunatravel.uz>

# SMS (Eskiz.uz)
ESKIZ_EMAIL=
ESKIZ_PASSWORD=

# To'lov (Click)
CLICK_SERVICE_ID=
CLICK_MERCHANT_ID=
CLICK_MERCHANT_USER_ID=
CLICK_SECRET_KEY=

# To'lov (Payme)
PAYME_MERCHANT_ID=
PAYME_SECRET_KEY=
PAYME_TEST_KEY=

# 2GIS xarita
DGIS_API_KEY=

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_SECRET=

# Apple OAuth
APPLE_CLIENT_ID=
APPLE_SECRET=
APPLE_KEY_ID=
APPLE_CERTIFICATE_KEY=

# Sentry (xatolik monitoring)
SENTRY_DSN=

# Sayt URL
SITE_URL=http://localhost:8008
```

---

## 4. Modellar

### accounts.User (Custom User — AbstractUser dan meros oladi)
| Maydon | Tur | Izoh |
|--------|-----|------|
| username | CharField | Unikal login |
| email | EmailField | Unikal, asosiy login |
| first_name, last_name | CharField | Ism familiya |
| phone | CharField | +998... telefon |
| avatar | ImageField | /media/avatars/ |
| role | CharField | user / admin |
| preferred_language | CharField | Til tanlovi (9 ta til) |
| created_at | DateTimeField | Ro'yxatdan o'tgan sana |

### regions.Region
| Maydon | Tur | Izoh |
|--------|-----|------|
| name | CharField | nomi (ko'p tilli: uz, ru, en, zh-hans, ar, de, fr, ja, ko) |
| slug | SlugField | URL uchun unikal |
| description | TextField | tavsifi (ko'p tilli) |
| image | ImageField | viloyat rasmi |
| is_active | BooleanField | faollik holati |
| order | PositiveIntegerField | tartib raqami |

### regions.Attraction
| Maydon | Tur | Izoh |
|--------|-----|------|
| region | FK -> Region | qaysi viloyatga tegishli |
| name | CharField | attraksiya nomi (ko'p tilli) |
| description | TextField | tavsif (ko'p tilli) |
| image | ImageField | rasm |
| latitude, longitude | DecimalField | GPS koordinatalar |
| is_active | BooleanField | faollik |
| order | PositiveIntegerField | tartib |

### tours.TourCategory
| Maydon | Tur | Izoh |
|--------|-----|------|
| name | CharField | kategoriya nomi (ko'p tilli) |
| slug | SlugField | unikal |
| icon | CharField | tabler icon |
| image | ImageField | kategoriya rasmi |

### tours.Tour
| Maydon | Tur | Izoh |
|--------|-----|------|
| title | CharField | tur nomi (ko'p tilli: uz, ru, en) |
| slug | SlugField | unikal, avtomatik yaratiladi |
| category | FK -> TourCategory | kategoriya |
| regions | M2M -> Region | qaysi viloyat(lar)da |
| attractions | M2M -> Attraction | attraksiyalar |
| description | TextField | to'liq tavsif (ko'p tilli) |
| short_description | CharField(500) | qisqa tavsif (ko'p tilli) |
| cover_image | ImageField | asosiy rasm |
| price | DecimalField | narx (USD) |
| price_uzs | DecimalField | narx (UZS) |
| duration_days | PositiveIntegerField | davomiylik (kun) |
| max_group_size | PositiveIntegerField | maksimal guruh (default: 15) |
| difficulty | CharField | easy/medium/hard |
| includes | TextField | narxga kiradi (ko'p tilli) |
| excludes | TextField | narxga kirmaydi (ko'p tilli) |
| itinerary | JSONField | marshrut (ko'p tilli) |
| is_active | BooleanField | faollik |
| is_featured | BooleanField | tavsiya etilgan |

### tours.TourImage
| Maydon | Tur | Izoh |
|--------|-----|------|
| tour | FK -> Tour | qaysi turga tegishli |
| image | ImageField | galereya rasmi |
| caption | CharField | rasm tavsifi |
| order | PositiveIntegerField | tartib |

### tours.ItineraryDay
| Maydon | Tur | Izoh |
|--------|-----|------|
| tour | FK -> Tour | qaysi turga |
| day | PositiveIntegerField | kun raqami |
| title | CharField | kun nomi |
| description | TextField | kun tavsifi |

### tours.CompanyStatistic
| Maydon | Tur | Izoh |
|--------|-----|------|
| number | CharField | "45+", "29K", "168K" |
| label | CharField | "Global Branches" (ko'p tilli) |
| order | PositiveIntegerField | tartib |

### tours.CompanyAdvantage
| Maydon | Tur | Izoh |
|--------|-----|------|
| icon | CharField | tabler icon |
| color | CharField | orange/blue/teal/purple |
| title | TextField | nomi (ko'p tilli) |
| description | TextField | tavsif (ko'p tilli) |
| order | PositiveIntegerField | tartib |

### bookings.Booking
| Maydon | Tur | Izoh |
|--------|-----|------|
| user | FK -> User | kim bron qilgan |
| tour | FK -> Tour | qaysi tur |
| booking_number | CharField | "BK" + UUID (avto) |
| status | CharField | pending/confirmed/cancelled/completed |
| travel_date | DateField | sayohat sanasi |
| num_adults | PositiveIntegerField | kattalar soni |
| num_children | PositiveIntegerField | bolalar soni |
| price_per_person | DecimalField | bir kishi uchun narx |
| total_price | DecimalField | umumiy narx |
| currency | CharField | USD (default) |
| special_requests | TextField | maxsus so'rovlar |
| cancellation_reason | TextField | bekor qilish sababi |
| cancelled_at | DateTimeField | bekor qilingan vaqt |

### payments.Currency
| Maydon | Tur | Izoh |
|--------|-----|------|
| code | CharField | USD, UZS, EUR |
| name | CharField | valyuta nomi |
| symbol | CharField | $, so'm |
| rate_to_usd | DecimalField | 1 USD = X valyuta |
| is_active | BooleanField | faollik |

### payments.Payment
| Maydon | Tur | Izoh |
|--------|-----|------|
| id | UUIDField | unikal ID (primary key) |
| booking | FK -> Booking | qaysi bron |
| user | FK -> User | kim to'lagan |
| method | CharField | click/payme/card/cash/paypal |
| status | CharField | created/pending/processing/paid/failed/cancelled/refunded |
| amount_uzs | DecimalField | miqdor (tiyinda) |
| amount_usd | DecimalField | miqdor (USD) |
| exchange_rate | DecimalField | kurs |
| gateway_transaction_id | CharField | gateway ID |
| gateway_response | JSONField | gateway javobi |
| card_last4 | CharField | karta oxirgi 4 raqami |
| card_brand | CharField | visa/mastercard/uzcard/humo |

### messages_app.ContactMessage
| Maydon | Tur | Izoh |
|--------|-----|------|
| user | FK -> User | autentifikatsiyadan o'tgan (ixtiyoriy) |
| name | CharField | ism |
| email | EmailField | email |
| phone | CharField | telefon |
| subject | CharField | mavzu |
| body | TextField | xabar matni |
| status | CharField | new/read/replied |
| reply_text | TextField | javob matni |
| replied_by | FK -> User | kim javob bergan |
| replied_at | DateTimeField | javob vaqti |

### reviews.Review
| Maydon | Tur | Izoh |
|--------|-----|------|
| user | FK -> User | kim yozgan |
| tour | FK -> Tour | qaysi tur uchun |
| rating | PositiveSmallIntegerField | 1-5 yulduz |
| title | CharField | sarlavha |
| body | TextField | izoh matni |
| is_approved | BooleanField | tasdiqlanganmi |
| Unique constraint: user + tour | | bir foydalanuvchi bir tur uchun faqat bir marta |

### places.NearbyPlace
| Maydon | Tur | Izoh |
|--------|-----|------|
| attraction | FK -> Attraction | qaysi attraksiya yonida |
| name | CharField | joy nomi |
| category | CharField | cafe/hotel/museum/pharmacy/atm/transport/other |
| address | CharField | manzil |
| latitude, longitude | DecimalField | koordinatalar |
| phone | CharField | telefon |
| rating | DecimalField | reyting |
| source | CharField | 2gis / google |
| external_id | CharField | tashqi ID |

---

## 5. URL Struktura

Barcha URL lar `i18n_patterns` ichida — til prefiksi bilan (`/uz/`, `/ru/`, `/en/` va h.k.)

```
/uz/                                 → Bosh sahifa
/uz/tours/                           → Turlar ro'yxati (qidiruv, filter, saralash)
/uz/tours/<slug>/                    → Tur tafsilotlari
/uz/regions/                         → Viloyatlar ro'yxati
/uz/regions/<slug>/                  → Viloyat tafsilotlari
/uz/bookings/                        → Mening bronlarim
/uz/bookings/<id>/                   → Bron tafsilotlari
/uz/bookings/create/<slug>/          → Bron yaratish
/uz/bookings/<id>/cancel/            → Bron bekor qilish
/uz/payments/<booking_id>/           → To'lov usulini tanlash
/uz/payments/<booking_id>/initiate/  → To'lovni boshlash
/uz/payments/<booking_id>/success/   → Muvaffaqiyat
/uz/payments/<booking_id>/failed/    → Xato
/uz/payments/return/<payment_id>/    → Gateway dan qaytish
/uz/payments/status/<payment_id>/    → AJAX holat so'rash (JSON)
/uz/payments/webhook/click/          → Click webhook (server-to-server)
/uz/payments/webhook/payme/          → Payme webhook (JSON-RPC)
/uz/payments/mock/<payment_id>/      → Mock to'lov (test uchun)
/uz/messages/contact/                → Bog'lanish formasi
/uz/messages/contact/success/        → Xabar yuborildi
/uz/messages/reply/<id>/             → Admin javobi (faqat staff)
/uz/reviews/create/<slug>/           → Sharh yozish
/uz/reviews/<id>/edit/               → Sharh tahrirlash
/uz/reviews/<id>/delete/             → Sharh o'chirish
/uz/accounts/signup/                 → Ro'yxatdan o'tish
/uz/accounts/login/                  → Kirish
/uz/accounts/logout/                 → Chiqish
/uz/accounts/profile/                → Profil
/uz/accounts/profile/edit/           → Profil tahrirlash
/uz/accounts/password/change/        → Parol o'zgartirish
/uz/accounts/google/login/           → Google OAuth
/uz/accounts/apple/login/            → Apple OAuth
/uz/places/nearby/                   → Yaqin joylar API (JSON, 30 daq cache)
/uz/places/attraction/<id>/nearby/   → Attraksiya atrofidagi joylar
/uz/solonasuperuse/                  → Admin panel
/uz/solonasuperuse/dashboard-stats/  → Dashboard API (JSON)
```

**Custom error handlerlar:**
- 404: `tours.views.custom_404_view` -> `404.html`
- 500: `tours.views.custom_500_view` -> `500.html`

---

## 6. Tillar

9 ta til qo'llab-quvvatlanadi:

| Kod | Til | Status |
|-----|-----|--------|
| uz | O'zbek | Asosiy til (LANGUAGE_CODE) |
| ru | Русский | To'liq |
| en | English | To'liq |
| zh-hans | 简体中文 | Mavjud |
| ar | العربية | Mavjud |
| de | Deutsch | Mavjud |
| fr | Français | Mavjud |
| ja | 日本语 | Mavjud |
| ko | 한국어 | Mavjud |

**`django-modeltranslation`** orqali quyidagi modellar tarjima qilinadi:
- `Region`: name, description
- `Attraction`: name, description
- `Tour`: title, description, short_description, includes, excludes, itinerary
- `TourCategory`: name
- `CompanyStatistic`: label
- `CompanyAdvantage`: title, description

**Fallback:** O'zbek -> Rus -> Ingliz

---

## 7. Async Vazifalar (Celery)

| Task | Fayl | Trigger |
|------|------|---------|
| `send_booking_confirmation_email` | bookings/tasks.py | Bron yaratilganda |
| `send_booking_cancellation_email` | bookings/tasks.py | Bron bekor qilinganda |
| `send_welcome_email` | accounts/tasks.py | Ro'yxatdan o'tganda (allauth signal) |
| `notify_admin_new_message` | messages_app/tasks.py | Contact form yuborilganda |
| `send_reply_email` | messages_app/tasks.py | Admin javob berganda |
| `send_booking_sms` | messages_app/tasks.py | Bron tasdiqlanganda (Eskiz.uz) |

**Yordamchi funksiya:** `send_sms_eskiz(phone, message)` — Eskiz.uz API orqali SMS yuborish.

**Celery sozlamalari:**
- Broker: Redis (redis://redis:6379/0)
- Serializer: JSON
- Beat scheduler: `django_celery_beat.schedulers:DatabaseScheduler`

---

## 8. To'lov Integratsiyasi

### Click
- **Docs:** https://docs.click.uz
- **Flow:** Sayt → Click checkout → `click/return/` → Tasdiqlash
- **Webhook:** `POST /uz/payments/webhook/click/` (Prepare + Complete)
- **Signature:** MD5 hash

### Payme
- **Docs:** https://developer.help.paycom.uz
- **Flow:** Sayt → Payme checkout → JSON-RPC webhook
- **Webhook:** `POST /uz/payments/payme/webhook/`
- **Auth:** Basic Auth (Merchant ID + Key)
- **Metodlar:** CheckPerformTransaction, CreateTransaction, PerformTransaction, CancelTransaction

### Mock mode
- `DEBUG=True` bo'lganda mock to'lov ishlaydi
- `/uz/payments/mock/<payment_id>/` orqali test qilish mumkin

---

## 9. Ijtimoiy Tarmoq Kirish (django-allauth)

### Google OAuth
1. [console.cloud.google.com](https://console.cloud.google.com) → Credentials → OAuth 2.0
2. Redirect URI: `https://solunatravel.uz/uz/accounts/google/login/callback/`
3. `.env` ga `GOOGLE_CLIENT_ID` va `GOOGLE_SECRET` qo'ying
4. Admin panelda: **Sites** → domain `solunatravel.uz` qo'ying
5. Admin panelda: **Social Applications** → Google app qo'ying

### Apple OAuth
1. [developer.apple.com](https://developer.apple.com) → Certificates, Identifiers & Profiles
2. `.env` ga `APPLE_CLIENT_ID`, `APPLE_SECRET`, `APPLE_KEY_ID`, `APPLE_CERTIFICATE_KEY` qo'ying

---

## 10. 2GIS Xarita

- **API:** https://docs.2gis.com/ru/api/search/get-started
- **Endpoint:** `GET /uz/places/nearby/?lat=41.2&lon=69.2&category=cafe&radius=1000`
- **Kategoriyalar:** cafe, hotel, museum, pharmacy, atm, transport, other
- **Cache:** 30 daqiqa (Django cache framework)
- **Kalitni olish:** https://partner.2gis.com

---

## 11. Dizayn Tizimi

### Front-end (Public sayt)
```css
/* Ranglar */
--green-deep:  #0D3B2E   /* Asosiy yashil */
--green-mid:   #1A5C45
--gold:        #C9A84C   /* Oltin accent */
--gold-light:  #E8C97A
--cream:       #FAF7F0   /* Fon */
--dark-footer: #071F18   /* Footer */

/* Shriftlar */
--font-display: 'Cormorant Garamond' (sarlavhalar)
--font-body:    'Jost' (matn)
```

### Admin panel (Karvon teması)
```css
/* Karvon (Caravan) — Forest & antique gold */
--bg: #F4EEE1;
--bg-card: #FFFDF8;
--text: #201D16;
--blue: #21412F;      /* Forest green — primary */
--gold: #B07F2E;      /* Antique gold — accent */
--green: #2E6E49;
--red: #9C4530;

/* Shriftlar */
--font: 'Public Sans' (body)
--font-display: 'Fraunces' (sarlavhalar, serif)
--font-mono: 'IBM Plex Mono' (raqamlar)
```

**Admin dizayn xususiyatlari:**
- Fixed header (position: fixed) — scroll qilganda yuqorida qoladi
- Gold dotted "route" chegarasi — Silk Road uslubida
- Frosted glass effekti (backdrop-filter: blur)
- Custom delete tugmalari (✕ ikonka)
- Inline tabular — responsive grid layout
- Skeleton loading animatsiyalari
- Dark mode qo'llab-quvvatlaydi

**Animatsiyalar (front-end):**
- Hero entrance: `opacity + translateY`, 200–800ms delay
- Scroll reveal: `.reveal`, `.reveal-left`, `.reveal-scale` + `.delay-1..5`
- Counter: 0 dan hisoblash (IntersectionObserver)
- Page transition: yashil overlay
- Navbar: scroll qilganda backdrop blur

---

## 12. Admin Panel

**URL:** `/uz/solonasuperuse/`  
**Custom Admin Site:** `SoLunaAdminSite`
**Dizayn:** macOS / MacBook uslubida

### Dizayn tizimi (admin.css):

**Ranglar:**
| Token | Light | Dark | vazifa |
|-------|-------|------|--------|
| `--bg` | #F5F5F7 | #1C1C1E | Asosiy fon |
| `--bg-card` | #FFFFFF | #2C2C2E | Kartochkalar |
| `--blue` | #007AFF | #0A84FF | Asosiy tugmalar (Save) |
| `--red` | #FF3B30 | #FF453A | O'chirish tugmalari |
| `--green` | #34C759 | #30D158 | Muvaffaqiyat |
| `--orange` | #FF9500 | #FF9F0A | Ogohlantirish |
| `--border` | #D2D2D7 | #48484A | Chegara chiziqlari |

**Shriftlar:** SF Pro (macOS system font)
**Burchaklar:** 6px, 8px, 10px, 12px, 16px
**Soyalar:** Yengil, subtle (0 1px 3px rgba(0,0,0,0.06))

### Header:
- `position: fixed` — scroll qilganda yuqorida qoladi
- `backdrop-filter: blur(20px)` — frosted glass effekti
- SoLuna branding + "Xush kelibsiz" + navigation tugmalari
- Chiqish tugmasi — qizil rang, hover'da to'liq qizil

### Sidebar:
- Clean white background
- Active item — ko'k fon (#007AFF)
- Add link — ko'k rang, hover'da to'liq ko'k
- Qidiruv maydoni — yumaloq burchakli

### Tugmalar:
- **Primary (Save):** Ko'k fon (#007AFF), oq matn
- **Secondary:** Oq fon, kul matn, chegara bilan
- **Delete:** Qizil fon (#FF3B30), oq matn
- **Cancel:** Oq fon, kul matn

### Inline tabular:
- Responsive grid layout (`repeat(auto-fill, minmax(180px, 1fr))`)
- Delete tugmasi — 30x30px qizil trash ikonka (SVG)
- Original/delete ustunlari yashirilgan

### Selector widget (filter_horizontal):
- Ikkita panel (Available / Chosen) yonma-yon
- 📋 / ✅ sarlavha ikonkalari
- Qidiruv maydonlari (Filtrlash placeholder)
- O'rtadagi tugmalar: Tanlash (ko'k), O'chirish (qizil)
- "Barchasini tanlash" / "Barchasini o'chirish" havolalari

### Dark mode:
- `data-theme="dark"` attribute orqali
- Barcha ranglar avtomatik moslashadi
- Theme toggle tugmasi header'da

### Mavjud bo'limlar:
- Accounts (Users, Groups)
- Regions (Regions, Attractions)
- Tours (Tours, Categories, Tour Images, Itinerary Days, Statistics, Advantages)
- Bookings (Bookings)
- Payments (Payments, Currencies)
- Messages App (Contact Messages)
- Reviews (Reviews)
- Places (Nearby Places)
- Periodic Tasks (Celery Beat)

### Dashboard:
- KPI kartalar (bronlar, xabarlar, turlar, izohlar)
- Tezkor harakatlar (tur qo'shish, region, xabarlar)
- Oxirgi bronlar va xabarlar ro'yxati
- To'lovlar, izohlar, viloyatlar
- Skeleton loading animatsiyalari

**Dashboard API:** `GET /uz/solonasuperuse/dashboard-stats/` (JSON)

### CSS fayl:
- `static/css/admin.css` — macOS teması (775+ qator)
- `collectstatic` orqali `staticfiles/css/admin.css` ga nusxalanadi

---

## 13. Production Deployment

### Nginx config:
```nginx
server {
    listen 80;
    server_name solunatravel.uz www.solunatravel.uz;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name solunatravel.uz www.solunatravel.uz;

    ssl_certificate /etc/letsencrypt/live/solunatravel.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/solunatravel.uz/privkey.pem;

    location /static/ { alias /app/staticfiles/; }
    location /media/  { alias /app/media/; }
    location / { proxy_pass http://web:8008; proxy_set_header Host $host; }
}
```

### SSL sertifikat:
```bash
certbot --nginx -d solunatravel.uz -d www.solunatravel.uz
```

### settings.py production uchun:
```python
DEBUG = False
ALLOWED_HOSTS = ['solunatravel.uz', 'www.solunatravel.uz']
# HTTPS redirect, secure cookies, XSS filter yoqilgan
```

---

## 14. Qolgan Ishlar

- [ ] Google OAuth kalitlarini sozlash
- [ ] Click/Payme merchant kalitlarini olish va ulash
- [ ] 2GIS API kalitini olish
- [ ] Eskiz.uz SMS kalitini olish
- [ ] `solunatravel.uz` domen ulash
- [ ] SSL sertifikat (Let's Encrypt)
- [ ] Nginx + Gunicorn production deploy
- [ ] Hero rasm (`/static/img/hero.jpg`) yuklash
- [ ] Admin paneldan regionlar va turlar qo'shish
- [ ] Ko'p tillik tarjimalar to'ldirish (uz, ru, en)
- [ ] Google Search Console ulash
- [ ] Backup strategiyasi (PostgreSQL dump — backup.sh mavjud)

---

## 15. Foydali Buyruqlar

```bash
# Loglar
docker compose logs -f web
docker compose logs -f celery

# Shell
docker compose run --rm web python manage.py shell

# Migration
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate

# Static fayllar
docker compose run --rm web python manage.py collectstatic --noinput

# Tarjima fayllarini yangilash
docker compose run --rm web python manage.py makemessages -l uz
docker compose run --rm web python manage.py compilemessages

# DB backup
./backup.sh

# DB restore
cat backups/backup.sql | docker compose exec -T db psql -U postgres tour_agency

# Deploy
./deploy.sh

# Restart
docker compose restart web
docker compose down && docker compose up -d
```

---

*SoLuna — Путешествия, наполненные солнцем и вдохновением* 🌙
