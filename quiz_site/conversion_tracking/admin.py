from django.contrib import admin

from conversion_tracking.models import ConversionExclusionsList, Pixel

# Register your models here.

admin.site.register(Pixel)
admin.site.register(ConversionExclusionsList)