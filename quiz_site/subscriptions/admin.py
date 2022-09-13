from django.contrib import admin

from subscriptions.models import SubscriptionChoices, UserPaymentStatus, UserSubscriptions

# Register your models here.


    #IF UPDATING REMEMBER TO MODIFY MODEL METHODS ALSO 
    # tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    # # new_user_free_trial_days = models.IntegerField(default=7)
    # renewal_frequency =  models.CharField(max_length=300, choices=subscription_choices)
    # stripe_renewal_frequency =  models.CharField(max_length=300, choices=stripe_interval_choices, null=True)

    # price =  models.DecimalField(max_digits=7, decimal_places=2, null=True)
    # price_before_sale =  models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    # stripe_price_id = models.CharField(max_length=300, null=True, blank=True)
    # currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL)
    # subscription_name = models.CharField(max_length=300, null=True)
    # feature_list = models.TextField(null=True, blank=True, max_length=10000,
    # default=
class SubscriptionChoiceAdmin(admin.ModelAdmin):
    list_display = ['tier',  'renewal_frequency', 'price', 'currency', 'stripe_price_id',  'subscription_name']


admin.site.register(UserPaymentStatus)
admin.site.register(UserSubscriptions)

admin.site.register(SubscriptionChoices, SubscriptionChoiceAdmin)