from django.contrib import admin
from .models import Region, Attraction
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline


class AttractionInline(TranslationStackedInline):
    model = Attraction
    extra = 1
    classes = ['collapse']


@admin.register(Region)
class RegionAdmin(TranslationAdmin):
    list_display = ['name', 'slug', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttractionInline]