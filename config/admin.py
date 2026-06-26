# config/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings


class SoLunaAdminSite(AdminSite):
    site_header = 'SoLuna Admin'
    site_title = 'SoLuna'
    index_title = 'Boshqaruv paneli'
    site_url = '/'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'phone_1', 'email_1']
    fieldsets = (
        ('Asosiy', {
            'fields': ('site_name', 'site_tagline')
        }),
        ('Aloqa ma\'lumotlari', {
            'fields': ('phone_1', 'phone_2', 'email_1', 'email_2', 'address', 'work_hours')
        }),
        ('Ijtimoiy tarmoqlar', {
            'fields': ('instagram', 'telegram', 'whatsapp', 'facebook')
        }),
        ('Promo banner', {
            'fields': ('promo_text', 'promo_cta_text', 'promo_cta_url')
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False