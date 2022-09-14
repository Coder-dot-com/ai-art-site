from django.db import models
from emails.models import UserEmail
from quiz_backend.models import UserSession

# Create your models here.



class Effect(models.Model):
    effect_name = models.CharField(max_length=500, unique=True)
    seed_phrase = models.CharField(max_length=500)
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

class CreateDesignRequest(models.Model):
    orientation = models.CharField(max_length=500, choices=orientation_choices)
    image = models.ImageField(upload_to='user_uploads/')
    effect = models.ForeignKey(Effect, on_delete=models.SET_NULL, null=True)
    email = models.ForeignKey(UserEmail, on_delete=models.SET_NULL, null=True)
    date_of_request = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=300, choices=status_choices)

