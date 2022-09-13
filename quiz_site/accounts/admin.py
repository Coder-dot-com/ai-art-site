from django.contrib import admin

from accounts.models import Profile, UserPreferenceType
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from quiz_backend.models import Referrer
# Register your models here.

admin.site.register(Profile)
admin.site.register(UserPreferenceType)


class NewUserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "date_joined",
        "display_latest_ref",
        "last_login",
        "is_staff",
    )

    list_display_links = ("id", "email")
    list_filter = ("last_login", "date_joined", "is_staff", "is_active")

    def display_latest_ref(self, obj):
        user_referrers = ""
        referrers = None
        
        if obj:
            
            referrers = Referrer.objects.filter(user_session__user=obj).order_by('time_created').reverse()

        if referrers:
            for ref in referrers:
                user_referrers += f"{ref.referrer} - {ref.audience} - {ref.ad} - <br>{ref.time_created.date()} {ref.time_created.strftime('%I:%M%p')} <br><hr>"
        return mark_safe(user_referrers)


admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)