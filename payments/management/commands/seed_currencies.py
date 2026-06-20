# payments/management/commands/seed_currencies.py
"""
Valyutalar va kurslarni yangilash.

Ishlatish:
  docker compose exec web python manage.py seed_currencies
  docker compose exec web python manage.py seed_currencies --update  # CBU'dan jonli kurs

Joylash:
  payments/management/__init__.py        (bo'sh)
  payments/management/commands/__init__.py (bo'sh)
  payments/management/commands/seed_currencies.py  ← bu fayl
"""
import requests
from decimal import Decimal
from django.core.management.base import BaseCommand
from payments.models import Currency


# Default kurslar (agar API ishlamasa)
DEFAULTS = [
    {'code': 'USD', 'name': 'US Dollar',     'symbol': '$', 'rate_to_usd': Decimal('1.0000')},
    {'code': 'UZS', 'name': 'Uzbek Som',     'symbol': "so'm", 'rate_to_usd': Decimal('12700.00')},
    {'code': 'EUR', 'name': 'Euro',          'symbol': '€', 'rate_to_usd': Decimal('0.92')},
    {'code': 'RUB', 'name': 'Russian Ruble', 'symbol': '₽', 'rate_to_usd': Decimal('90.50')},
]


class Command(BaseCommand):
    help = 'Valyuta va kurslarni seed qilish/yangilash'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true',
                            help='CBU API\'dan jonli kurslarni yuklash')

    def handle(self, *args, **opts):
        # Default qiymatlardan boshlaymiz
        for d in DEFAULTS:
            obj, created = Currency.objects.update_or_create(
                code=d['code'],
                defaults={
                    'name': d['name'],
                    'symbol': d['symbol'],
                    'rate_to_usd': d['rate_to_usd'],
                    'is_active': True,
                },
            )
            mark = "✓ yaratildi" if created else "↺ yangilandi"
            self.stdout.write(f"  {mark}  {d['code']}: 1 USD = {d['rate_to_usd']} {d['code']}")

        # Jonli kurslar (CBU API)
        if opts['update']:
            self.stdout.write("\n🌐 CBU'dan jonli kurslarni yuklash...")
            try:
                r = requests.get('https://cbu.uz/uz/arkhiv-kursov-valyut/json/', timeout=10)
                r.raise_for_status()
                rates = r.json()

                code_map = {'USD': 'USD', 'EUR': 'EUR', 'RUB': 'RUB'}
                for item in rates:
                    ccy = item.get('Ccy')
                    if ccy not in code_map:
                        continue
                    rate_uzs = Decimal(item.get('Rate', '0'))
                    if ccy == 'USD':
                        # UZS ni yangilaymiz: 1 USD = X UZS
                        Currency.objects.filter(code='UZS').update(rate_to_usd=rate_uzs)
                        self.stdout.write(f"  ✓ UZS: 1 USD = {rate_uzs}")
                    elif ccy in ('EUR', 'RUB'):
                        # Cross: USD vs ccy
                        # CBU: 1 ccy = rate_uzs UZS
                        # We need: 1 USD = X ccy → X = uzs_rate / ccy_rate
                        try:
                            uzs = Currency.objects.get(code='UZS')
                            cross = uzs.rate_to_usd / rate_uzs
                            Currency.objects.filter(code=ccy).update(rate_to_usd=cross)
                            self.stdout.write(f"  ✓ {ccy}: 1 USD = {cross:.4f}")
                        except Currency.DoesNotExist:
                            pass
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  ✗ CBU API xatosi: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ {Currency.objects.count()} ta valyuta DBda."))