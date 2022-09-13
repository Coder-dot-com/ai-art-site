from datetime import datetime, timedelta, timezone

from django.urls import reverse
from emails.tasks import subscription_cancelled
from tiers.models import Tier
from subscriptions.models import UserPaymentStatus, UserSubscriptions
from django.contrib import messages

def user_subscription_valid(request):
    expiry_date = None
    subscribe_url = reverse('subscription_page_dashboard')
    user_subscription = None
    user = request.user
    try:
        user_payment_status = UserPaymentStatus.objects.get(user=user)
    except:
        return dict(checked_subscription=True)

    print("Checking subscription")

        #The trigger for this function should be context_processors which checks for logged in,
        #user has an active User payment status and current time > subscription expiry,
        #been more than 60 minutes since last sync

    try:
        user_subscription = UserSubscriptions.objects.filter(
                user_payment_status=user_payment_status,
                ).latest('created_at')
    except UserSubscriptions.DoesNotExist:
        pass
    if user_payment_status.status == "active" and datetime.now(timezone.utc) > (user_payment_status.subscription_expiry + timedelta(seconds=60)) and datetime.now(timezone.utc) > (user_payment_status.last_synced + timedelta(seconds=1)):
        response = user_payment_status.sync_subscription_expiry()
        if response == "Canceled":
            try:
                subscription_cancelled.delay(user_subscription.subscription_id, failed_payment=True)
            except Exception as b:
                print(b)
 
    elif user_payment_status.status == "free":
        pass

        # messages.error(request, f"""Subscription expired. <a href='{subscribe_url}'>Subscribe</a>
        # today to enjoy all benefits""")
 
    elif user_payment_status.status == "free_trial":

        if user_payment_status.subscription_expiry.replace(tzinfo=None) < datetime.utcnow().replace(tzinfo=None):
            user_payment_status.status == "free"
            # Also set tier to free
            tier = Tier.objects.get(type='free_tier')
            user_payment_status.tier = tier

            user_payment_status.save()

 
        else:
            expiry_date = datetime.strftime(user_payment_status.subscription_expiry, '%Y-%m-%d')

            # messages.error(request, f"""Free trial active. Expires on: {expiry_date}. <a href='{subscribe_url}'>Subscribe</a>
            # today to enjoy all benefits""")       
    
        pass

    #Add check for free trial subscription and display as message with days remaining
    #With link to subscribe on all dashboard pages(i.e. add to header
    # Same if susbcription expired/not valid
    
    if user_subscription:
        return dict(checked_subscription=True, user_subscription=user_subscription, user_payment_status=user_payment_status, subscribe_url=subscribe_url, expiry_date=expiry_date)

    else:
        return dict(checked_subscription=True, user_payment_status=user_payment_status, subscribe_url=subscribe_url, expiry_date=expiry_date)

