from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ['home', ]

    def location(self, item):
        return reverse(item)




# Example dynamic sitemap with models
# class ArticleSitemap(Sitemap):
#     changefreq = "weekly"
#     priority = 0.5  (#0.5 for non money pages, 0.9 for higher)
#     protocol = 'https'

#     def items(self):
#         return Article.objects.all()

#     def lastmod(self, obj):  (timestamp/last modified is important)
#         return obj.article_published
        
#     def location(self,obj):
#         return '/blog/%s' % (obj.article_slug)
