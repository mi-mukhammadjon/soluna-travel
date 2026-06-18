# SoLuna Touroperator — Project Handoff

**Loyiha:** SoLuna — O'zbekiston bo'yicha premium tur agentlik web sayti  
**Brend:** SoLuna (soluna.uz)  
**Egasi:** Oygul Axatova — Touroperator  
**Stack:** Django 4.2 + PostgreSQL + Redis + Celery + Docker  
**Sana:** Iyun 2025

---

## 1. Arxitektura

```
tour_agency/
├── config/               # Django settings, urls, celery
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── accounts/             # Custom User, login, register, profil
├── regions/              # Viloyatlar va attraksiyalar
├── tours/                # Turlar, kategoriyalar, galereya
├── bookings/             # Bronlar, bekor qilish
├── payments/             # Click + Payme integratsiya
├── messages_app/         # Contact form, email/SMS javob
├── reviews/              # Reyting va izohlar
├── places/               # 2GIS yaqin joylar API
├── templates/            # HTML templatelar
│   ├── admin/            # Custom admin panel
│   ├── accounts/         # Login, register, profil
│   ├── tours/            # List, detail
│   ├── regions/          # List, detail
│   ├── bookings/         # List, detail, create
│   ├── payments/         # Select payment
│   └── messages_app/     # Contact form
├── static/css/main.css   # SoLuna premium CSS
├── wheels/               # Offline Python packages
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
└── wait_for_db.py
```

---

## 2. Docker Servislar

| Servis | Image | Port | Vazifa |
|--------|-------|------|--------|
| web | python:3.11-slim | 8000 | Django server |
| db | postgres:15-alpine | 5432 | Ma'lumotlar bazasi |
| redis | redis:7-alpine | 6379 | Cache + Celery broker |
| celery | python:3.11-slim | — | Async vazifalar (email, SMS) |
| celery_beat | python:3.11-slim | — | Periodic tasks scheduler |

### Ishga tushirish
```bash
# .env faylni to'ldiring
cp .env.example .env

# Build va ishga tushirish
docker compose up -d --build

# Migrations
docker compose run --rm web python manage.py migrate

# Superuser yaratish
docker compose run --rm web python manage.py createsuperuser

# Static fayllar
docker compose run --rm web python manage.py collectstatic --noinput

# Holat
docker compose ps
docker compose logs -f web
```

---

## 3. .env O'zgaruvchilar

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=soluna.uz,www.soluna.uz

# Database
DB_NAME=tour_agency
DB_USER=postgres
DB_PASSWORD=strong-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=oygulakhatovas@gmail.com
EMAIL_HOST_PASSWORD=app-password
DEFAULT_FROM_EMAIL=SoLuna <oygulakhatovas@gmail.com>

# SMS (Eskiz.uz)
ESKIZ_EMAIL=oygulakhatovas@gmail.com
ESKIZ_PASSWORD=eskiz-password

# To'lov
CLICK_SERVICE_ID=
CLICK_MERCHANT_ID=
CLICK_SECRET_KEY=
PAYME_ID=
PAYME_KEY=

# 2GIS xarita
DGIS_API_KEY=your-2gis-key

# Google OAuth (allauth)
GOOGLE_CLIENT_ID=
GOOGLE_SECRET=

# Sayt URL
SITE_URL=https://soluna.uz
```

---

## 4. Modellar

### accounts.User
| Maydon | Tur | Izoh |
|--------|-----|------|
| username | CharField | Unikal |
| email | EmailField | Unikal |
| first_name, last_name | CharField | |
| phone | CharField | +998... |
| avatar | ImageField | /media/avatars/ |
| role | CharField | user / admin |
| preferred_language | CharField | uz, ru, en... |
| is_verified | BooleanField | Email tasdiqlash |
| email_verification_token | UUIDField | |

### regions.Region
`name`, `slug`, `description`, `image`, `is_active`, `order`  
Ko'p tillik: `name_uz`, `name_ru`, `name_en`, `name_zh_hans`, `name_ar`, `name_de`, `name_fr`, `name_ja`, `name_ko`

### regions.Attraction
`region (FK)`, `name`, `description`, `image`, `latitude`, `longitude`, `is_active`

### tours.Tour
`title`, `slug`, `category (FK)`, `regions (M2M)`, `attractions (M2M)`, `description`, `short_description`, `cover_image`, `price (USD)`, `price_uzs`, `duration_days`, `max_group_size`, `difficulty`, `includes`, `excludes`, `itinerary (JSON)`, `is_active`, `is_featured`

### bookings.Booking
`user (FK)`, `tour (FK)`, `booking_number`, `status`, `travel_date`, `num_adults`, `num_children`, `price_per_person`, `total_price`, `special_requests`  
Status: `pending → confirmed → completed / cancelled`

### payments.Payment
`booking (FK)`, `provider (click/payme/cash)`, `status`, `amount (UZS)`, `transaction_id`, `provider_transaction_id`, `provider_response (JSON)`

### messages_app.ContactMessage
`name`, `email`, `phone`, `subject`, `body`, `status (new/read/replied)`, `reply_text`, `replied_by (FK)`

### reviews.Review
`user (FK)`, `tour (FK)`, `rating (1-5)`, `title`, `body`, `is_approved`  
Unique: user + tour

### places.NearbyPlace
`attraction (FK)`, `name`, `category (cafe/hotel/museum...)`, `latitude`, `longitude`, `phone`, `rating`, `source (2gis)`, `external_id`

---

## 5. URL Struktura

```
/uz/                          → Bosh sahifa
/uz/tours/                    → Turlar ro'yxati (filtr, qidiruv)
/uz/tours/<slug>/             → Tur detail
/uz/regions/                  → Viloyatlar
/uz/regions/<slug>/           → Viloyat detail
/uz/bookings/                 → Mening bronlarim
/uz/bookings/<id>/            → Bron detail
/uz/bookings/create/<slug>/   → Bron yaratish
/uz/bookings/<id>/cancel/     → Bekor qilish
/uz/payments/<booking_id>/    → To'lov usulini tanlash
/uz/payments/click/return/    → Click qaytish
/uz/payments/click/webhook/   → Click webhook (server-to-server)
/uz/payments/payme/webhook/   → Payme webhook (JSON-RPC)
/uz/messages/contact/         → Bog'lanish formasi
/uz/reviews/create/<slug>/    → Izoh yozish
/uz/accounts/register/        → Ro'yxatdan o'tish
/uz/accounts/login/           → Kirish
/uz/accounts/profile/         → Profil
/uz/places/nearby/            → Yaqin joylar API
/uz/admin/                    → Admin panel
```

---

## 6. Tillar

9 ta til qo'llab-quvvatlanadi:

| Kod | Til |
|-----|-----|
| uz | O'zbek |
| ru | Русский |
| en | English |
| zh-hans | 中文 |
| ar | العربية |
| de | Deutsch |
| fr | Français |
| ja | 日本語 |
| ko | 한국어 |

**`django-modeltranslation`** orqali quyidagi modellar tarjima qilinadi:
- `Region`: name, description
- `Attraction`: name, description
- `Tour`: title, description, short_description, includes, excludes, itinerary
- `TourCategory`: name

Tarjima qo'shish uchun admin panelda har bir maydon uchun alohida til varianti ko'rinadi.

---

## 7. Async Vazifalar (Celery)

| Task | Fayl | Trigger |
|------|------|---------|
| `send_booking_confirmation_email` | bookings/tasks.py | Bron yaratilganda |
| `send_booking_cancellation_email` | bookings/tasks.py | Bron bekor qilinganda |
| `send_verification_email` | accounts/tasks.py | Ro'yxatdan o'tganda |
| `send_welcome_email` | accounts/tasks.py | Ro'yxatdan o'tganda |
| `notify_admin_new_message` | messages_app/tasks.py | Contact form yuboriLganda |
| `send_reply_email` | messages_app/tasks.py | Admin javob berganda |
| `send_booking_sms` | messages_app/tasks.py | Bron tasdiqlanganda |

---

## 8. To'lov Integratsiyasi

### Click
- **Docs:** https://docs.click.uz
- **Flow:** Sayt → Click checkout → `click/return/` → Tasdiqlash
- **Webhook:** `POST /uz/payments/click/webhook/` (Prepare + Complete)
- **Signature:** MD5 hash

### Payme
- **Docs:** https://developer.help.paycom.uz
- **Flow:** Sayt → Payme checkout → JSON-RPC webhook
- **Webhook:** `POST /uz/payments/payme/webhook/`
- **Auth:** Basic Auth (Merchant ID + Key)
- **Metod larni:** CheckPerformTransaction, CreateTransaction, PerformTransaction, CancelTransaction

---

## 9. Ijtimoiy Tarmoq Kirish (django-allauth)

### Google OAuth
1. [console.cloud.google.com](https://console.cloud.google.com) → Credentials → OAuth 2.0
2. Redirect URI: `https://soluna.uz/uz/accounts/google/login/callback/`
3. `.env` ga `GOOGLE_CLIENT_ID` va `GOOGLE_SECRET` qo'ying
4. Admin panelda: **Sites** → domain `soluna.uz` qo'ying
5. Admin panelda: **Social Applications** → Google app qo'ying

---

## 10. 2GIS Xarita

- **API:** https://docs.2gis.com/ru/api/search/get-started
- **Endpoint:** `GET /uz/places/nearby/?lat=41.2&lon=69.2&category=cafe&radius=1000`
- **Kategoriyalar:** cafe, hotel, museum, pharmacy, atm
- **Cache:** 30 daqiqa (Django cache framework)
- **Kalitni olish:** https://partner.2gis.com

---

## 11. Dizayn Tizimi

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

**Animatsiyalar:**
- Hero entrance: `opacity + translateY`, 200–800ms delay
- Scroll reveal: `.reveal`, `.reveal-left`, `.reveal-scale` + `.delay-1..5`
- Counter: 0 dan hisoblash (IntersectionObserver)
- Page transition: yashil overlay
- Navbar: scroll qilganda backdrop blur

---

## 12. Production Deployment (Keyingi qadam)

### Nginx config kerak:
```nginx
server {
    listen 80;
    server_name soluna.uz www.soluna.uz;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name soluna.uz www.soluna.uz;

    ssl_certificate /etc/letsencrypt/live/soluna.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/soluna.uz/privkey.pem;

    location /static/ { alias /app/staticfiles/; }
    location /media/  { alias /app/media/; }
    location / { proxy_pass http://web:8000; proxy_set_header Host $host; }
}
```

### `settings.py` production uchun:
```python
DEBUG = False
ALLOWED_HOSTS = ['soluna.uz', 'www.soluna.uz']

# Gunicorn (runserver o'rniga)
# entrypoint.sh da:
# exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### SSL sertifikat:
```bash
certbot --nginx -d soluna.uz -d www.soluna.uz
```

---

## 13. Admin Panel

**URL:** `/uz/admin/`  
**Mavjud bo'limlar:**
- Accounts (Users)
- Regions (Regions, Attractions)
- Tours (Tours, Categories, Images)
- Bookings (Bookings)
- Payments (Payments)
- Messages App (Contact Messages)
- Reviews (Reviews)
- Places (Nearby Places)
- Periodic Tasks (Celery Beat)

**Dashboard:** KPI kartalar, tezkor harakatlar, oxirgi bronlar va xabarlar

---

## 14. Qolgan Ishlar

- [ ] Google OAuth kalitlarini sozlash
- [ ] Click/Payme merchant kalitlarini olish va ulash
- [ ] 2GIS API kalitini olish
- [ ] Eskiz.uz SMS kalitini olish
- [ ] `soluna.uz` domen ulash
- [ ] SSL sertifikat (Let's Encrypt)
- [ ] Nginx + Gunicorn production deploy
- [ ] Hero rasm (`/static/img/hero-bg.jpg`) yuklash
- [ ] Admin paneldan regionlar va turlar qo'shish
- [ ] Ko'p tillik tarjimalar to'ldirish (uz, ru, en)
- [ ] Google Search Console ulash
- [ ] Backup strategiyasi (PostgreSQL dump)

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

# Tarjima fayllarini yangilash
docker compose run --rm web python manage.py makemessages -l uz
docker compose run --rm web python manage.py compilemessages

# DB backup
docker compose exec db pg_dump -U postgres tour_agency > backup.sql

# DB restore
cat backup.sql | docker compose exec -T db psql -U postgres tour_agency

# Restart
docker compose restart web
docker compose down && docker compose up -d
```

---

*SoLuna — Путешествия, наполненные солнцем и вдохновением* 🌙
