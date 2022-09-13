from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class UserEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(max_length=300, unique=True)
    promo_consent = models.BooleanField(default=False)
    date_time_added = models.DateTimeField(auto_now_add=True)

    #has signal listening for create to sync with sendinblue


class SentEmail(models.Model):
    recipient = models.ForeignKey(UserEmail, null=True, on_delete=models.SET_NULL)
    sent_from_email =  models.CharField(max_length=200)
    sent_from_name = models.CharField(max_length=200, blank=True)
    email_to_field = models.CharField(max_length=5000)
    email_subject = models.CharField(max_length=300)
    email_content = models.CharField(max_length=5000)
