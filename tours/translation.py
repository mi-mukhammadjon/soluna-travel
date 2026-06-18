from modeltranslation.translator import register, TranslationOptions
from .models import Tour, TourCategory

@register(Tour)
class TourTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'short_description', 'includes', 'excludes', 'itinerary')

@register(TourCategory)
class TourCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)