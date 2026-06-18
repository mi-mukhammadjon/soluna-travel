from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'email', 'phone', 'role',
        'is_verified', 'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'email_verification_token', 'avatar_preview']

    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha', {
            'fields': (
                'phone', 'avatar', 'avatar_preview',
                'role', 'preferred_language',
                'is_verified', 'email_verification_token',
                'created_at'
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
    avatar_preview.short_description = 'Avatar'