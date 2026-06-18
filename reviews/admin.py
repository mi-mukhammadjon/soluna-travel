from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'tour', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    list_editable = ['is_approved']
    search_fields = ['user__email', 'tour__title', 'body']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} ta izoh tasdiqlandi.")
    approve_reviews.short_description = "Tanlangan izohlarni tasdiqlash"

    def reject_reviews(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} ta izoh bekor qilindi.")
    reject_reviews.short_description = "Tanlangan izohlarni bekor qilish"