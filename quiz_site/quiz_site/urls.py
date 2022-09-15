"""quiz_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf.urls.static import static
from . import views
from django.views.generic.base import TemplateView #import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticSitemap 


from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap as wgsitemap

sitemaps = {
      'static':StaticSitemap, #add StaticSitemap to the dictionary
      'wagtail': wgsitemap,
}


urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),  
    path('tinymce/', include('tinymce.urls')),
    path("", views.home, name="home"),
    path('admin/1a/', admin.site.urls),
    path('quiz/', include('quiz_backend.urls')),
    path('currency', include('multicurrency.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('subscribe/', include('subscriptions.urls')),
    path('emails/', include('emails.urls')),

    path('lp/', include('landing_page.urls')),

    # path('about/', views.about, name='about'), 
    # path('contact/', views.contact, name='contact'), 
    path('termsandconditions/', views.tandc, name='tandc'), 
    path('privacypolicy/', views.privpolicy, name='privpolicy'), 
    path('deliveryinfo/', views.deliveryinfo, name='deliveryinfo'), 
    path('refundandcancellationpolicy/', views.refundpolicy, name='refundpolicy'), 
    path('postdata/', include('conversion_tracking.urls')),

    re_path("robots.txt\/?$",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),  #add the robots.txt file
    path('create/', include('create_design.urls')),
    path('created_design/buy', include('create_design_buy.urls')),

    #wgatail urls
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('blog/<slug>/', views.redirect_old_blog, name="redirect_old_blog"),
    path('', include(wagtail_urls)),
    #end wagtail


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
