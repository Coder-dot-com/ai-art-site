from django.contrib import admin

from .models import BuyOptions, CreateDesignRequest, Effect

# Register your models here.

class BuyOptionAdmin(admin.ModelAdmin):
    list_display = ['type_of_purchase', 'orientation', 'size', 'price', 'price_before_sale']


admin.site.register(CreateDesignRequest)
admin.site.register(Effect)
admin.site.register(BuyOptions, BuyOptionAdmin)
