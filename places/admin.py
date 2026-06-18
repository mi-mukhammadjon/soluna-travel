from django.contrib import admin
from .models import NearbyPlace


@admin.register(NearbyPlace)
class NearbyPlaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'address', 'rating', 'source', 'is_active']
    list_filter = ['category', 'source', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'address']
    readonly_fields = ['external_id', 'source', 'created_at']