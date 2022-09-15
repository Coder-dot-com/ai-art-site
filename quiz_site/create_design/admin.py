from django.contrib import admin

from .models import BuyOptions, CreateDesignRequest, Effect, ShippingOptions

# Register your models here.

admin.site.register(CreateDesignRequest)
admin.site.register(Effect)
admin.site.register(BuyOptions)
admin.site.register(ShippingOptions)