from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'status', 'created_at', 'reply_button']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'body']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'body', 'user', 'created_at']

    fieldsets = (
        ('Xabar', {
            'fields': ('user', 'name', 'email', 'phone', 'subject', 'body', 'created_at')
        }),
        ('Javob', {
            'fields': ('status', 'reply_text', 'replied_at', 'replied_by')
        }),
    )

    def reply_button(self, obj):
        if obj.status != 'replied':
            url = reverse('messages_app:reply', args=[obj.pk])
            return format_html('<a class="button" href="{}">Javob berish</a>', url)
        return format_html('<span style="color:green;">✓ Javob berildi</span>')
    reply_button.short_description = 'Javob'

    def save_model(self, request, obj, form, change):
        if change and 'reply_text' in form.changed_data and obj.reply_text:
            import django.utils.timezone as tz
            obj.status = 'replied'
            obj.replied_at = tz.now()
            obj.replied_by = request.user
            super().save_model(request, obj, form, change)
            from .tasks import send_reply_email
            send_reply_email.delay(obj.pk)
        else:
            super().save_model(request, obj, form, change)