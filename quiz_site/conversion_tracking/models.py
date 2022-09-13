from django.db import models
from quiz_backend.models import Category

# Create your models here.
pixel_types = [
    ("facebook", "facebook"),
    ("tiktok", "tiktok"),


]


class Pixel(models.Model):
    category =  models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    pixel_id = models.CharField(max_length=7000, unique=True)
    pixel_type = models.CharField(max_length=1000, choices=pixel_types)
    conv_api_token = models.CharField(max_length=7000, null=True, blank=True)


class ConversionExclusionsList(models.Model):
    ip = models.CharField(blank=True, max_length=2000, null=True)
    user_agent = models.CharField(blank=True, max_length=2000, null=True)


