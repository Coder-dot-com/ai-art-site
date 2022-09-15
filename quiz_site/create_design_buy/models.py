from django.db import models

from create_design.models import BuyOptions, CreateDesignRequest
from quiz_backend.models import UserSession
from multicurrency.models import Currency
from emails.models import UserEmail
# Create your models here.

class Order(models.Model):
    STATUS = (
        ('created', 'created'),
        ('paid', 'paid'),
        ('completed', 'completed'),
    )
    session = models.ForeignKey(UserSession, null=True, on_delete=models.SET_NULL)
    order_subtotal = models.DecimalField(max_digits=7, decimal_places=2,)
    order_total = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    one_usd_to_currency_conv_rate_when_placed = models.FloatField(blank=True, null=True, default=1)
    email = models.ForeignKey(UserEmail, on_delete=models.SET_NULL, null=True)
    status = models.CharField(choices=STATUS, max_length=300)
    order_number = models.CharField(max_length=200, unique=True, null=True)
    order_note = models.CharField(max_length=100, blank=True)

    shipping_method = models.CharField(max_length=200, null=True)
    shipping_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    ship_first_name = models.CharField(max_length=50, blank=True)
    ship_last_name = models.CharField(max_length=50, blank=True)
    ship_address_line_1 = models.CharField(max_length=15, blank=True)
    ship_address_line_2 = models.CharField(max_length=50, blank=True)
    ship_country = models.CharField(max_length=50, blank=True)
    ship_state = models.CharField(max_length=50, blank=True)
    ship_city = models.CharField(max_length=50, blank=True)
    ship_postcode = models.CharField(max_length=50, blank=True)
    
    payment_intent_id = models.CharField(max_length=300, null=True, blank=True)    

    order_conf_email_sent = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(BuyOptions, null=True, on_delete=models.SET_NULL)
    design_request = models.ForeignKey(CreateDesignRequest, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    pass


class ShippingOption(models.Model):
    option = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    def __str__(self):
        return self.option