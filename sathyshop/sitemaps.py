from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    protocol = "https"      # IMPORTANT for SEO
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            'home',
            'about',
            'contact',
            'store',
            

        ]

    def location(self, item):
        return reverse(item)