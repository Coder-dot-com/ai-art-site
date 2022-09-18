import os
import time
from uuid import uuid4
from django.db import models
from emails.models import UserEmail
from quiz_backend.models import UserSession
import boto3
from decouple import config
from quiz_site.settings import AWS_STORAGE_BUCKET_NAME, BASE_DIR
from multicurrency.models import Currency
# Create your models here.



class Effect(models.Model):
    effect_name = models.CharField(max_length=500, unique=True)
    prompt = models.CharField(max_length=500)
    prompt_strength = models.FloatField()
    active = models.BooleanField(default=True)
    before_image = models.ImageField(upload_to='effects/before/', null=True, blank=True)
    after_image = models.ImageField(upload_to='effects/after/', null=True, blank=True)

    def __str__(self) -> str:
        return self.effect_name

orientation_choices = [
    ("Landscape", "Landscape"),
    ("Portrait", "Portrait"),
    ("Square", "Square"),
]

effect_choices = [
    ("Landscape", "Landscape"),
    ("Portrait", "Portrait"),
    ("Square", "Square"),
]

status_choices = [
    ("requested", "requested"),
    ("created", "created"),
]

def random_id():
    return uuid4()

class CreateDesignRequest(models.Model):
    orientation = models.CharField(max_length=500, choices=orientation_choices)
    image = models.ImageField(upload_to='user_uploads/')
    effect = models.ForeignKey(Effect, on_delete=models.SET_NULL, null=True)
    email = models.ForeignKey(UserEmail, on_delete=models.SET_NULL, null=True)
    date_of_request = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=300, choices=status_choices)
    created_design = models.ImageField(upload_to='created_designs/', null=True, blank=True)
    design_preview = models.ImageField(upload_to='design_previews/', null=True, blank=True)
    unique_id = models.CharField(default=random_id, max_length=300)



buy_choices = [
    ("Canvas", "Canvas"),
    ("Print", "Print"),
    ("Digital", "Digital")
]

class BuyOptions(models.Model):
    type_of_purchase = models.CharField(max_length=300, choices=buy_choices)
    orientation = models.CharField(max_length=500, choices=orientation_choices, null=True, blank=True)
    size =  models.CharField(max_length=500, null=True, blank=True)
    price =  models.DecimalField(max_digits=7, decimal_places=2, null=True)
    price_before_sale =  models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    
