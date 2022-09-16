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

    def clean_created_design_download(self):

        #download cleaned image from s3
        s3 = boto3.client('s3', aws_access_key_id=config('AWS_ACCESS_KEY_ID'), aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))
        # No need for env path with base_dir
        file_name = str(((self.created_design.name).split("/"))[-1])

        if str(BASE_DIR) == "/APP/quiz_site":
            download_path = f"/django/quiz_site/media/tmp/{file_name}"
        else:       
            download_path = f"{BASE_DIR}/media/tmp/{file_name}"
        
        def _download_from_s3():
            print(os.path.abspath(__file__))
            print("download path is", download_path)
            s3.download_file(f'{AWS_STORAGE_BUCKET_NAME}-resized', self.created_design.name , download_path)

            if os.path.exists(download_path):
                pass
            else:
                try:
                    _download_from_s3()
                except:
                    print("S3 download failed")
                    print("waiting 3 seconds")
                    time.sleep(3)
                    print("retrying s3 download")
                    _download_from_s3()

            _download_from_s3()
            return download_path

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
    
