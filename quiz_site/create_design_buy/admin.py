from django.contrib import admin

from .models import Order, ShippingOption

# Register your models here.

admin.site.register(ShippingOption)
admin.site.register(Order)