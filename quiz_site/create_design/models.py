from django.db import models
from emails.models import UserEmail
from quiz_backend.models import UserSession

# Create your models here.

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

class CreateDesignRequest(models.Model):
    orientation = models.CharField(max_length=500, choices=orientation_choices)
    image = models.ImageField(upload_to='user_uploads/')
    effect = models.CharField(max_length=500, choices=effect_choices)
    email = models.ForeignKey(UserEmail, on_delete=models.SET_NULL, null=True)
    date_of_request = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=300, choices=status_choices)
