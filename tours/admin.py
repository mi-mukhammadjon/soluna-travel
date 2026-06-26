from django.contrib import admin
from django.utils.html import format_html
from .models import Tour, TourCategory, TourImage, CompanyStatistic, CompanyAdvantage
from modeltranslation.admin import TranslationAdmin

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px; border-radius:4px;">', obj.image.url)
        return '-'
    preview.short_description = 'Preview'


@admin.register(TourCategory)
class TourCategoryAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tour)
class TourAdmin(TranslationAdmin):
    list_display = ['title', 'price', 'discount_display', 'duration_days', 'difficulty',
                    'is_active', 'is_featured', 'is_recommended', 'review_count_display', 'created_at']
    list_editable = ['is_active', 'is_featured', 'is_recommended']
    list_filter = ['is_active', 'is_featured', 'is_recommended', 'difficulty', 'category', 'regions']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['regions', 'attractions']
    inlines = [TourImageInline]
    readonly_fields = ['created_at', 'updated_at', 'cover_preview']

    fieldsets = (
        ('Asosiy', {
            'fields': ('title', 'slug', 'category', 'short_description', 'description')
        }),
        ('Rasm', {
            'fields': ('cover_image', 'cover_preview')
        }),
        ('Narx va davomiylik', {
            'fields': ('price', 'price_uzs', 'child_price_percent', 'duration_days', 'max_group_size', 'difficulty')
        }),
        ('Joylar', {
            'fields': ('regions', 'attractions')
        }),
        ('Tarkib', {
            'fields': ('includes', 'excludes', 'itinerary'),
            'classes': ('collapse',)
        }),
        ('Maxsus taklif / Chegirma', {
            'fields': ('discount_percent', 'discount_label', 'discount_until'),
            'description': "Chegirma foizini kiriting (0–90). Yakuniy narx avtomatik hisoblanadi va bron narxiga ham qo'llanadi."
        }),
        ('Holat', {
            'fields': ('is_active', 'is_featured', 'is_recommended', 'created_at', 'updated_at')
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:200px; border-radius:8px;">',
                obj.cover_image.url
            )
        return '-'
    cover_preview.short_description = 'Joriy rasm'

    def review_count_display(self, obj):
        return obj.review_count
    review_count_display.short_description = 'Reviews'

    def discount_display(self, obj):
        if obj.has_discount:
            return format_html(
                '<b style="color:#d9480f;">−{}%</b> → ${}',
                obj.discount_percent, obj.discounted_price
            )
        return '—'
    discount_display.short_description = 'Chegirma'


@admin.register(CompanyStatistic)
class CompanyStatisticAdmin(TranslationAdmin):
    list_display = ('number', 'label', 'order')
    list_editable = ('order',)

@admin.register(CompanyAdvantage)
class CompanyAdvantageAdmin(TranslationAdmin):
    list_display = ('title', 'icon', 'color', 'order')
    list_editable = ('order',)