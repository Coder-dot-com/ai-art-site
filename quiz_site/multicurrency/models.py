from django.db import models
import requests
from decouple import config
import datetime as dt


# Create your models here.

#Need to add choices for currency code

currency_choices = [
    ("USD", "USD"),
    ("AUD", "AUD"),
    ("GBP", 'GBP'),
    ('CAD', 'CAD'),
    ('NZD', 'NZD'),
    ('EUR', 'EUR'),

]



class Currency(models.Model):
    currency_display_name = models.CharField(max_length=100, unique=True)
    currency_code = models.CharField(max_length=100, unique=True, choices=currency_choices)
    currency_symbol = models.CharField(max_length=2)
    one_usd_to_currency_rate = models.FloatField(blank=True, null = True)
    last_updated_rate = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__ (self):
        return self.currency_code

    def check_to_update_rate(self):
        if self.currency_code == "USD":
            print("Can't update rate for USD")
        else:
            time_diff = dt.datetime.now().replace(tzinfo=None) - self.last_updated_rate.replace(tzinfo=None)
            print(time_diff.days)

            try:
                if (time_diff.days) > float(1):
                    print("been long time since rate update")
                    self.update_rate()
            except Exception as e:
                print(e)
                print("Error updating currency conv rate")


    def update_rate(self):
       #async the update
       #Later on switch to celery beat and schedule daily
        if not self.currency_code == "USD":

            api_key = config('CURRENCY_CONV_API_KEY1')
            print(api_key)

            try:

                url = f'https://api.freecurrencyapi.com/v1/latest?apikey={api_key}'
                response = requests.get(url)
                print(response)
                data = response.json()
                print(data)
                usd_to_currency_rate = float(data['data'][self.currency_code])
                print(usd_to_currency_rate)
                self.one_usd_to_currency_rate = usd_to_currency_rate
                
                self.last_updated_rate = dt.datetime.now()
                print("currency conv succeeded")
            except Exception as e:
                print("Currency conversion failed")
                print(e)
  

        else: 
            self.one_usd_to_currency_rate = 1
        pass

    def save(self, *args, **kwargs):
        self.update_rate()
        super(Currency, self).save(*args, **kwargs)
    
    def usd_to_currency_rounded(self, usd_amount):
            usd_amount = float(usd_amount)
            #Return the rounded amount same as on frontend
            # return round(round(usd_amount * self.one_usd_to_currency_rate), 2) - 0.01
            return round(round(usd_amount * self.one_usd_to_currency_rate), 2)
