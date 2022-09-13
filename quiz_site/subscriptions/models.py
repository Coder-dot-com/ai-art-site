from datetime import  datetime, timedelta, timezone
from django.db import models
from django.contrib.auth import get_user_model
import stripe
from multicurrency.models import Currency
from quiz_site.settings import STRIPE_SECRET_KEY
from django.db.models import Q

from colorfield.fields import ColorField

from tiers.models import Tier
# Create your models here.

User = get_user_model()
stripe.api_key = STRIPE_SECRET_KEY

choices = [
    ("free_trial", "free_trial"),
    ("active", "active"),
    ("free", "free"),
]

def default_date_time():
    now = datetime.now()
    return now - timedelta(days=100)


class UserPaymentStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    tier = models.ForeignKey(Tier, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=300, choices=choices)
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    add_free_trial_days = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(default=default_date_time)
    # has_had_free_trial = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.subscription_expiry and self.status == "free_trial":
            self.subscription_expiry = datetime.utcnow() + timedelta(days = 7)
        super(UserPaymentStatus, self).save(*args, **kwargs)
    

    #For now manually set page_expiry for renewed subscription
    

    def sync_subscription_expiry(self):
        print("Syncing subscription...")
        #Call stripe api using subscription id from latest


        
        # Add if statement to only run below if not true
        # I.e,. check if current time greater than subscription_expiry
        if self.subscription_expiry.replace(tzinfo=None) <  datetime.now().replace(tzinfo=None):
            try:
                user_subscription = UserSubscriptions.objects.filter(Q(
                    user_payment_status=self,
                    status="paid")| Q(user_payment_status=self,
                    status="created")).latest('created_at')

            except UserSubscriptions.DoesNotExist:
                user_subscription = None
            if user_subscription:
                

                self.tier = user_subscription.subscription_choice.tier
                self.save()

                subscription = stripe.Subscription.retrieve(
                    user_subscription.subscription_id,
                    )
                
                next_payment_due = datetime.utcfromtimestamp(subscription['current_period_end'])
                if (subscription['status']) == "trialing" or "active":
                    self.status = "active"
                    self.subscription_expiry = next_payment_due
                    self.last_synced = datetime.now(timezone.utc)
                    self.save()
                    user_subscription.status = "paid"
                    user_subscription.next_due =  next_payment_due
                    user_subscription.latest_response = subscription
                    user_subscription.interval_start_date = datetime.utcfromtimestamp(subscription['current_period_start'])
                    user_subscription.save()

                else:
                    try:
                        stripe.Subscription.modify(
                        user_subscription.subscription_id,
                        cancel_at_period_end=True
                            )

                        user_subscription.status = "cancelled"
                        user_subscription.save()
                        print("Subscription cancelled")
                        self.status = 'free'
                        self.save()

                        return "Canceled"
                        

                    except Exception as e:
                        
                        print(e)
                        print("Exception occured cancelling subscription after sync expiry")




        
 

    


subscription_choices = [
    ("monthly", "monthly"),
    ("annually", "annually"),
]

stripe_interval_choices = [
    ("month", "month"),
    ("year", "year"),
]


class SubscriptionChoices(models.Model):
    #IF UPDATING REMEMBER TO MODIFY MODEL METHODS ALSO 
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    # new_user_free_trial_days = models.IntegerField(default=7)
    renewal_frequency =  models.CharField(max_length=300, choices=subscription_choices)
    stripe_renewal_frequency =  models.CharField(max_length=300, choices=stripe_interval_choices, null=True)

    price =  models.DecimalField(max_digits=7, decimal_places=2, null=True)
    price_before_sale =  models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=300, null=True, blank=True)
    currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL)
    subscription_name = models.CharField(max_length=300, null=True)
    feature_list = models.TextField(null=True, blank=True, max_length=10000,
    default=
    """

                                        <div class="plan-features mt-4">
                                            <p class="font-size-15"><i class="mdi mdi-checkbox-marked-circle text-success font-size-16 me-2 align-middle"></i><b>Unlimited</b>
                                                Target Audience</p>
                                            <p class="font-size-15"><i class="mdi mdi-checkbox-marked-circle text-success font-size-16 me-2 align-middle"></i><b>1</b>
                                                User Account</p>
                                            <p class="font-size-15"><i class="mdi mdi-checkbox-marked-circle text-success font-size-16 me-2 align-middle"></i><b>100+</b>
                                                Video Tuts</p>
                                            <p class="font-size-15"><i class="mdi mdi-close-circle text-danger font-size-16 me-2 align-middle"></i><b>Public</b>
                                                Displays
                                            </p>
                                        </div>
    """)
    description = models.TextField(max_length=1000, blank=True, null=True)
    create_nonusd_subscriptions = models.BooleanField(default=False)
    has_badge = models.BooleanField(default=False)
    badge_color = ColorField(null=True, blank=True, format="hexa")
    badge_text_color = ColorField(null=True, blank=True, format="hexa")
    badge_text = models.CharField(max_length=100, null=True, blank=True)

    def create_update_other_currencies(self):
        #will use save method to call this if selected and then reset trigger

        
        #Get all currency objects and update rate
        currencies = Currency.objects.all().exclude(currency_code="USD")

        for currency in currencies:
            currency.check_to_update_rate()
            prod_id = stripe.Price.retrieve(self.stripe_price_id).product
            # prod_id = stripe.Product.create(name=f"{self.subscription_name}_{self.renewal_frequency}_{currency.currency_code}").id
            new_price = currency.usd_to_currency_rounded(self.price)
            new_price_stripe = int(100 * new_price)
            if self.price_before_sale:
                new_price_before_sale = currency.usd_to_currency_rounded()
            else: 
                new_price_before_sale = None
            #Create stripe plan
            stripe_id = stripe.Price.create(
            unit_amount=new_price_stripe,
            currency=str(currency.currency_code).lower(),
            recurring={"interval": f"{self.stripe_renewal_frequency}"},
            product=prod_id,
            ).id



            #Get or Create subscriptionchoice object
            subscription_choice_obj = SubscriptionChoices.objects.get_or_create(currency=currency,
            renewal_frequency=self.renewal_frequency, tier=self.tier)[0]
            
            
            subscription_choice_obj.stripe_renewal_frequency=self.stripe_renewal_frequency
            subscription_choice_obj.price=new_price_stripe/100
            subscription_choice_obj.price_before_sale=new_price_before_sale
            subscription_choice_obj.stripe_price_id=stripe_id
            subscription_choice_obj.subscription_name=self.subscription_name
            subscription_choice_obj.feature_list=self.feature_list
            subscription_choice_obj.description=self.description
            subscription_choice_obj.has_badge = self.has_badge
            subscription_choice_obj.badge_color = self.badge_color
            subscription_choice_obj.badge_text = self.badge_text

            subscription_choice_obj.save()

            

        #Create trigger and reset
            #Also on save allow creation of stripe subscription propduct automatically if no product id supplied
            # for any currency chosen

        #Test/frontend

        #Transfer to template

    def save(self, *args, **kwargs):

        if self.create_nonusd_subscriptions and self.currency.currency_code == "USD":
            self.create_update_other_currencies()
            self.create_nonusd_subscriptions = False
        
        if not self.stripe_price_id:
            pass

        super(SubscriptionChoices, self).save(*args, **kwargs)



subscription_statuses = [
    ("created", "created"),
    ("paid", "paid"),
    ("unpaid", "unpaid"),
    ("cancelled", "cancelled"),
    ("downgraded", "downgraded"),
    ("upgraded", "upgraded"),


]

class UserSubscriptions(models.Model):
    user_payment_status = models.ForeignKey(UserPaymentStatus, on_delete=models.SET_NULL, null=True)
    subscription_choice = models.ForeignKey(SubscriptionChoices, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=300, choices=subscription_statuses)

    date_subscribed = models.DateTimeField(auto_now_add=True)
    stripe_customer_id = models.CharField(max_length=300)    
    payment_intent_id = models.CharField(max_length=300, null=True,blank=True)
    subscription_id = models.CharField(max_length=300, null=True, blank=True)

    interval_start_date = models.DateTimeField(null=True, blank=True) 
    next_due = models.DateTimeField()
    payment_method = models.CharField(max_length=300)
    amount_subscribed =  models.DecimalField(max_digits=7, decimal_places=2)
    renewal_frequency =  models.CharField(max_length=300)
    currency_code = models.CharField(max_length=300) 
    created_at = models.DateTimeField(auto_now_add=True)
    latest_response = models.CharField(max_length=5000, blank=True, null=True)
    subscription_confirmation_email_sent = models.BooleanField(default=False)
    
 


