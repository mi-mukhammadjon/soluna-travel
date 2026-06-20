from modeltranslation.translator import register, TranslationOptions
from .models import Tour, TourCategory, CompanyStatistic, CompanyAdvantage

@register(Tour)
class TourTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'short_description', 'includes', 'excludes', 'itinerary')

@register(TourCategory)
class TourCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(CompanyStatistic)
class CompanyStatisticTranslationOptions(TranslationOptions):
    fields = ('label',) # Raqam tarjima qilinmaydi, faqat yozuv

@register(CompanyAdvantage)
class CompanyAdvantageTranslationOptions(TranslationOptions):
    fields = ('title', 'description')