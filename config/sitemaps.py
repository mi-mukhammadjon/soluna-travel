"""
Sitemap'lar — qidiruv tizimlari (Google, Yandex) sahifalarni topishi uchun.
i18n=True → har bir sahifa 9 tilda alohida URL sifatida ro'yxatga olinadi.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from tours.models import Tour
from regions.models import Region


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    i18n = True
    protocol = "https"

    def items(self):
        return ["home", "tours:tour-list", "regions:region-list"]

    def location(self, item):
        return reverse(item)


class TourSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"
    i18n = True
    protocol = "https"

    def items(self):
        return Tour.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("tours:tour-detail", kwargs={"slug": obj.slug})

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None)


class RegionSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"
    i18n = True
    protocol = "https"

    def items(self):
        return Region.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("regions:region-detail", kwargs={"slug": obj.slug})


SITEMAPS = {
    "static": StaticViewSitemap,
    "tours": TourSitemap,
    "regions": RegionSitemap,
}
