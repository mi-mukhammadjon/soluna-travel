import os
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk

# 1. Avval BASE_DIR ni aniqlab olamiz
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Keyin .env faylining aniq manzilini ko'rsatib yuklaymiz
load_dotenv(dotenv_path=BASE_DIR / '.env')

# 3. O'zgaruvchilarni chaqiramiz
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# Debugni bool tipiga o'tkazish (To'g'ri yozgansiz)
# Faqat 'True' degan so'z kelsagina True bo'ladi, aks holda False
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS dagi ortiqcha bo'shliqlarni olib tashlaydigan variant
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS').split(',')]
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',           # allauth uchun shart

    # Third-party
    'rest_framework',
    'django_celery_beat',

    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',

    # Local apps
    'accounts',
    'regions',
    'tours',
    'bookings',
    'payments',
    'places',
    'messages_app',
    'reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # allauth uchun shart
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'tour_agency'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# --------------------------------------------------------------------------
# django-allauth sozlamalari
# --------------------------------------------------------------------------
ACCOUNT_LOGIN_METHODS = {'email'}           # email bilan login
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'optional'     # 'mandatory' qilsangiz email tasdiqlanadi
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'secret': os.getenv('GOOGLE_SECRET', ''),
        }
    },
    'apple': {
        'APP': {
            'client_id': os.getenv('APPLE_CLIENT_ID', ''),
            'secret': os.getenv('APPLE_SECRET', ''),
            'key': os.getenv('APPLE_KEY_ID', ''),
            'certificate_key': os.getenv('APPLE_CERTIFICATE_KEY', ''),
        }
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'uz'

LANGUAGES = [
    ('uz', 'O\'zbek'),
    ('ru', 'Русский'),
    ('en', 'English'),
    ('zh-hans', '中文'),
    ('ar', 'العربية'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('ja', '日本語'),
    ('ko', '한국어'),
    ('es', 'Spanish'),
]

# Agar biron bir maydon tanlangan tilda to'ldirilmagan bo'lsa, standart o'zbek tilidagi qiymat ko'rinadi
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('uz', 'ru', 'en'),
}

TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Yoki o'zingizning papkangiz nomi
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@touragency.uz')

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL', '')
ESKIZ_PASSWORD = os.getenv('ESKIZ_PASSWORD', '')

CLICK_MERCHANT_ID = os.environ.get('CLICK_MERCHANT_ID', '')
CLICK_SERVICE_ID = os.environ.get('CLICK_SERVICE_ID', '')
CLICK_SECRET_KEY = os.environ.get('CLICK_SECRET_KEY', '')
CLICK_MERCHANT_USER_ID = os.environ.get('CLICK_MERCHANT_USER_ID', '')
 
# Ro'yxatdan o'tish: https://business.payme.uz/
PAYME_MERCHANT_ID = os.environ.get('PAYME_MERCHANT_ID', '')
PAYME_SECRET_KEY = os.environ.get('PAYME_SECRET_KEY', '')
PAYME_TEST_KEY = os.environ.get('PAYME_TEST_KEY', '')  # Sandbox uchun

DGIS_API_KEY = os.getenv('DGIS_API_KEY', '')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# ════ LOGGING ════
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },

    },
    'loggers': {
        'payments': {
            'handlers': ['console'], # BU YERDA FAQAT 'console' QOLSIN!
            'level': 'INFO',
            'propagate': True,
        },
        # Boshqa ilovalar bo'lsa, ularda ham faqat 'console' qolsin
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
 

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# HTTPS sozlamalari
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    "https://solunatravel.uz",
    "https://www.solunatravel.uz",
    # Agar alohida frontend domeningiz bo'lsa, uni ham qo'shasiz
]

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DNS', ''),
    traces_sample_rate=1.0,
    send_default_pii=True,
)