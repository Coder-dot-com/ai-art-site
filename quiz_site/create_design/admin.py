from django.contrib import admin

from .models import CreateDesignRequest, Effect

# Register your models here.

admin.site.register(CreateDesignRequest)
admin.site.register(Effect)