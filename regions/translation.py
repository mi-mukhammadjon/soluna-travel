from modeltranslation.translator import register, TranslationOptions
from .models import Region, Attraction


@register(Region)
class RegionTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Attraction)
class AttractionTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
