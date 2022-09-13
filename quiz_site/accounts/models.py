from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    email_confirmed = models.BooleanField(default=False) 
    reset_password = models.BooleanField(default=False)

    class Meta:
        app_label = 'auth'


class UserPreferenceType(models.Model):
    preference_name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.preference_name




