from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'provider', 'status', 'amount', 'currency', 'paid_at', 'created_at']
    list_filter = ['provider', 'status', 'created_at']
    search_fields = ['booking__booking_number', 'transaction_id', 'provider_transaction_id']
    readonly_fields = ['transaction_id', 'provider_transaction_id', 'provider_response', 'created_at', 'updated_at']

    fieldsets = (
        ('Bron', {'fields': ('booking',)}),
        ('To\'lov', {'fields': ('provider', 'status', 'amount', 'currency', 'paid_at')}),
        ('Tranzaksiya', {'fields': ('transaction_id', 'provider_transaction_id', 'provider_response')}),
        ('Vaqt', {'fields': ('created_at', 'updated_at')}),
    )