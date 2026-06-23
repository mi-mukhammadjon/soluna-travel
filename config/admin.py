# config/admin.py

from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class SoLunaAdminSite(AdminSite):
    site_header = 'SoLuna Admin'
    site_title = 'SoLuna'
    index_title = 'Boshqaruv paneli'
    site_url = '/'