# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'rate_to_usd', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    list_editable = ('rate_to_usd', 'is_active')
    search_fields = ('code', 'name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'short_id', 'booking_link', 'method', 'status_badge',
        'amount_display', 'card_info', 'created_at', 'paid_at',
    )
    list_filter = ('status', 'method', 'created_at')
    search_fields = (
        'id', 'booking__booking_number', 'user__email',
        'gateway_transaction_id',
    )
    readonly_fields = (
        'id', 'booking', 'user', 'amount_uzs', 'amount_usd',
        'exchange_rate', 'gateway_transaction_id', 'gateway_response',
        'card_last4', 'card_brand', 'created_at', 'paid_at', 'cancelled_at',
    )

    fieldsets = (
        ('Asosiy', {
            'fields': ('id', 'booking', 'user', 'method', 'status'),
        }),
        ('Pul', {
            'fields': ('amount_uzs', 'amount_usd', 'exchange_rate'),
        }),
        ('Gateway', {
            'fields': ('gateway_transaction_id', 'gateway_response', 'card_brand', 'card_last4'),
            'classes': ('collapse',),
        }),
        ('Vaqt', {
            'fields': ('created_at', 'paid_at', 'cancelled_at'),
            'classes': ('collapse',),
        }),
    )

    def short_id(self, obj):
        return str(obj.id)[:8] + '...'
    short_id.short_description = 'ID'

    def booking_link(self, obj):
        if obj.booking:
            return format_html(
                '<a href="/admin/bookings/booking/{}/change/">{}</a>',
                obj.booking.id, obj.booking.booking_number,
            )
        return '—'
    booking_link.short_description = 'Booking'

    def amount_display(self, obj):
        return format_html(
            '<strong>{} UZS</strong><br><small>${}</small>',
            obj.amount_uzs_formatted,
            obj.amount_usd,
        )
    amount_display.short_description = 'Amount'

    def card_info(self, obj):
        if obj.card_brand and obj.card_last4:
            return f"{obj.card_brand.upper()} **** {obj.card_last4}"
        return '—'
    card_info.short_description = 'Card'

    def status_badge(self, obj):
        colors = {
            'created': ('#94A3B8', '#fff'),
            'pending': ('#F59E0B', '#fff'),
            'processing': ('#3B82F6', '#fff'),
            'paid': ('#10B981', '#fff'),
            'failed': ('#E24B4A', '#fff'),
            'cancelled': ('#64748B', '#fff'),
            'refunded': ('#8B5CF6', '#fff'),
        }
        bg, fg = colors.get(obj.status, ('#999', '#fff'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:50px;font-size:0.75rem;font-weight:700;">{}</span>',
            bg, fg, obj.get_status_display(),
        )
    status_badge.short_description = 'Status'

    actions = ['mark_as_paid_manual', 'mark_as_cancelled']

    def mark_as_paid_manual(self, request, queryset):
        count = 0
        for p in queryset.filter(status__in=('created', 'pending', 'processing')):
            p.mark_paid(transaction_id=f'manual-{p.id}', gateway_data={'admin_user': request.user.username})
            count += 1
        self.message_user(request, f"{count} ta to'lov paid qilindi.")
    mark_as_paid_manual.short_description = "Tanlanganlarni paid qilish (manual)"

    def mark_as_cancelled(self, request, queryset):
        count = queryset.exclude(status__in=('paid', 'refunded')).update(status='cancelled')
        self.message_user(request, f"{count} ta to'lov cancelled qilindi.")
    mark_as_cancelled.short_description = "Tanlanganlarni cancelled qilish"