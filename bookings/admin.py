from django.contrib import admin
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_number', 'user_email', 'tour', 'travel_date',
        'num_adults', 'total_price', 'status', 'created_at'
    ]
    list_filter = ['status', 'travel_date', 'created_at']
    search_fields = ['booking_number', 'user__email', 'tour__title']
    list_editable = ['status']
    readonly_fields = ['booking_number', 'price_per_person', 'total_price', 'created_at', 'updated_at']
    date_hierarchy = 'travel_date'

    fieldsets = (
        ('Bron', {'fields': ('booking_number', 'status', 'user', 'tour')}),
        ('Sayohat', {'fields': ('travel_date', 'num_adults', 'num_children', 'special_requests')}),
        ('Narx', {'fields': ('price_per_person', 'total_price', 'currency')}),
        ('Bekor qilish', {'fields': ('cancellation_reason', 'cancelled_at'), 'classes': ('collapse',)}),
        ('Vaqt', {'fields': ('created_at', 'updated_at')}),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'