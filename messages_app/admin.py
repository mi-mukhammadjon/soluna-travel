from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactMessage, NewsletterSubscriber, Newsletter


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


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at', 'sent_at']

    def send_newsletter(self, request, queryset):
        from .tasks import send_newsletter_email
        for newsletter in queryset.filter(status='draft'):
            send_newsletter_email.delay(newsletter.pk)
        self.message_user(request, f"{queryset.filter(status='draft').count()} ta xabar yuborilmoqda.")
    send_newsletter.description = "Tanlangan xabarlarni yuborish"
    actions = [send_newsletter]
