from django.contrib import admin

from emails.models import SentEmail, UserEmail

# Register your models here.

admin.site.register(SentEmail)
admin.site.register(UserEmail)