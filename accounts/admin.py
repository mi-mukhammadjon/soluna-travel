from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, SiteSettings

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'phone', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'avatar_preview']

    # Allauth emailni tasdiqlaganini ko'rsatish uchun:
    # list_display da user.emailaddress_set.filter(primary=True, verified=True).exists() ni ishlatish tavsiya qilinadi

    fieldsets = UserAdmin.fieldsets + (
        (_('Дополнительная информация'), {
            'fields': (
                'phone', 'avatar', 'avatar_preview',
                'role', 'preferred_language', 'created_at'
            )
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:60px; height:60px; border-radius:50%; object-fit:cover;">',
                obj.avatar.url
            )
        return '—'
    avatar_preview.short_description = _('Аватар')


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