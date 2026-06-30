"""
templatetags/lang_tags.py
─────────────────────────
Til kodidan native nomini olish uchun custom filter.

Joylash:
  myapp/templatetags/lang_tags.py   ← shu fayl
  myapp/templatetags/__init__.py    ← bo'sh fayl

Templatega yuklash:
  {% load lang_tags %}
"""
from django import template

register = template.Library()

# Har bir tilning O'Z TILIDA yozilgan nomi
NATIVE_NAMES = {
    'en': 'English',
    'ru': 'Русский',
    'uz': "O'zbekcha",
    'ko': '한국어',
    'ja': '日本語',
    'zh': '中文',
    'zh-hans': '简体中文',
    'zh-hant': '繁體中文',
    'ar': 'العربية',
    'tr': 'Türkçe',
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español',
    'it': 'Italiano',
    'pt': 'Português',
    'pt-br': 'Português (BR)',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'kk': 'Қазақша',
    'ky': 'Кыргызча',
    'tg': 'Тоҷикӣ',
    'fa': 'فارسی',
    'hi': 'हिन्दी',
    'vi': 'Tiếng Việt',
    'th': 'ไทย',
    'id': 'Bahasa Indonesia',
    'ms': 'Bahasa Melayu',
    'tk': 'Türkmen',
    'az': 'Azərbaycanca',
    'hy': 'Հայերեն',
    'ka': 'ქართული',
    'he': 'עברית',
    'uk': 'Українська',
    'be': 'Беларуская',
    'sv': 'Svenska',
    'no': 'Norsk',
    'da': 'Dansk',
    'fi': 'Suomi',
    'cs': 'Čeština',
    'sk': 'Slovenčina',
    'hu': 'Magyar',
    'ro': 'Română',
    'bg': 'Български',
    'el': 'Ελληνικά',
}

@register.filter(name='get_native_name')
def get_native_name(code):
    """Til kodidan native nomini qaytaradi. Topilmasa kod o'zi qaytariladi."""
    return NATIVE_NAMES.get(code.lower(), code.upper())


import re

# includes / excludes matnini alohida bandlarga ajratadigan ajratuvchilar
_ITEM_SPLIT_RE = re.compile(r'[;\n\r•]+')


@register.filter(name='split_items')
def split_items(value):
    """Matnni o'qishga oson bandlarga ajratadi.

    `;`, yangi qator yoki `•` belgilari bo'yicha bo'lib, har bir bandning
    bosh/oxiridagi probel va ortiqcha belgilarni tozalaydi. Bo'sh bandlar
    tashlab yuboriladi. Templateda checklist ko'rinishida ishlatiladi:

        {% for item in tour.includes|split_items %}
            <li><i class="ti ti-check"></i> {{ item }}</li>
        {% endfor %}
    """
    if not value:
        return []
    items = []
    for raw in _ITEM_SPLIT_RE.split(str(value)):
        # bosh/oxiridagi probel, ro'yxat belgilari va band oxiridagi nuqtani tozalaymiz
        item = raw.strip().lstrip('•-–—*').strip().rstrip('.。،')
        if item:
            items.append(item)
    return items