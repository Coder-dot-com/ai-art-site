from django.db import models
from tinymce.models import HTMLField

# Create your models here.


class SiteSettings(models.Model):
    site_email = models.EmailField(max_length=300, null=True, blank=True)
    site_logo = models.ImageField(upload_to="logo/", null=True, blank=True)
    site_logo_square = models.ImageField(upload_to="logo/", null=True, blank=True)
    site_name = models.CharField(max_length=100, null=True, blank=True)
    site_slogan = models.CharField(max_length=100, null=True, blank=True)
    site_icon = models.ImageField(upload_to="logo/", null=True, blank=True)
    site_meta_tags = models.TextField(max_length=2000, null=True, blank=True)
    site_global_analytics = models.TextField(max_length=2000, null=True, blank=True)
    site_signup_copy_title = models.TextField(max_length=2000, null=True, blank=True)
    site_signup_copy = HTMLField(max_length=2000, null=True, blank=True)
    site_button_css = models.TextField(max_length=2000, null=True, blank=True)
    site_button_hover_css = models.TextField(max_length=2000, null=True, blank=True)
    site_button_focus_css = models.TextField(max_length=2000, null=True, blank=True)
    site_headings_css = models.TextField(max_length=2000, null=True, blank=True)

