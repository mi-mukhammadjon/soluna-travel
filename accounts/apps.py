from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = _('Пользователи и доступы') # Admin panelda ko'rinadigan chiroyli nom

    def ready(self):
        # Allauth signallari ishlashi uchun chaqirib qo'yamiz
        import accounts.signals