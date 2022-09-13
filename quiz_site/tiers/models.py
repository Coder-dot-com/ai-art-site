from django.db import models
from colorfield.fields import ColorField
# Create your models here.

tier_choices = (
    ('free_tier', 'free_tier'),
    ('starter', 'starter'),
    ('professional', 'professional'),
    ('business', 'business'),
    ('enterprise', 'enterprise'),


)


class Tier(models.Model):
    type = models.CharField(choices=tier_choices, unique=True, max_length=200)
    display_name = models.CharField(max_length=200)
    tier_ranking = models.IntegerField(unique=True)
    badge_color = ColorField(null=True, blank=True, format="hexa")

    def __str__(self):
        return self.display_name
