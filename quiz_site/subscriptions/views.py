from uuid import uuid4
from django.shortcuts import redirect, render
from django.urls import reverse
import stripe
from accounts.models import Profile
from emails.tasks import subscription_cancelled, subscription_confirmed_email
from quiz_backend.models import Response
from .models import UserPaymentStatus, UserSubscriptions, SubscriptionChoices, UserPaymentStatus, UserSubscriptions
from quiz_site.settings import STRIPE_ENDPOINT_SECRET, STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from quiz_backend.views import _session

from django.http import HttpResponse
from django.shortcuts import  render
from django.db.models import Q

# from emails.tasks import subscription_confirmed_email


from django.views.decorators.csrf import csrf_exempt
import stripe
from conversion_tracking.tasks import conversion_tracking

from datetime import datetime, timedelta, timezone


stripe.api_key = STRIPE_SECRET_KEY

stripe_pub_key = STRIPE_PUBLIC_KEY


# Create your views here.
@login_required
def stripe_payment_subscibe(request, option_id):
    context = {}
    user = request.user
    profile_obj = Profile.objects.get(user=user)
    # Page = Page
    print(profile_obj)

    user_email = user.email

    customer = stripe.Customer.create(
    email=user_email)
    print('customer', customer)
    customer_id = customer.id
    print(customer_id)

    subscription_choice = SubscriptionChoices.objects.get(id=option_id)
    price = subscription_choice.price
    currency_code = subscription_choice.currency.currency_code

    price_id = subscription_choice.stripe_price_id
    trial_period_days= 0
     # Keep at 0 for now otherwise no payment intent
    #And also means free trail functionality is kept in app
    #  allowing easier payment provider switch
    active_cancelled_subscription = None


    #Get the page payment status object or create
    try:
        user_payment_status = UserPaymentStatus.objects.get(user=user)
        

        user_subscription = None
        if user_payment_status.status == "active":

            try:
                
                user_subscription = UserSubscriptions.objects.get(user_payment_status=user_payment_status, status="paid")
            
                if user_subscription:
                    #Here render the subscription and ability to cancel    
                    return HttpResponse("<h5 class='text-center'>A subscription is already active for this account, please cancel it and try again</h5>")
            except:
                pass


    #Then check if page status is currently active or not if active check if there is already an 
    # active subscription if active subscription then just display the current subscription
        #Then same check will also be added on subscription page load for the display part

    except UserPaymentStatus.DoesNotExist:
        user_payment_status = UserPaymentStatus.objects.create(user=user,status="free")


    try:


        user_subscription = UserSubscriptions.objects.filter(
            user_payment_status=user_payment_status,
            status="cancelled", 

            ).latest('created_at')

        try:
            # Check if higher tier cancelled subscription available
            user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                        user_payment_status=user_payment_status,
                        status="cancelled"),
                        next_due__gt= datetime.now(),
                        subscription_choice__tier__tier_ranking__gte=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                            'subscription_choice__tier__tier_ranking')).reverse()[0]
            if user_subscription_with_greater_tier.next_due.replace(tzinfo=None)  > datetime.now().replace(tzinfo=None):
                    user_subscription = user_subscription_with_greater_tier
                    
        except:
            pass
        
    except:
        pass
    current_time = datetime.now(timezone.utc)
    if user_subscription:

        start_date = user_subscription.next_due
        print(start_date)


        # Need to delay days even if user is resubscribing to ensure new susbcription only starts after
        days_left = int((start_date - current_time).days)
        print('days_left', days_left)

        # Here need to convert days to new plan only if tier gte to current 
        if subscription_choice.tier.tier_ranking >= user_subscription.subscription_choice.tier.tier_ranking:
            
            print("Subscription greater")

            if user_subscription.subscription_choice.stripe_renewal_frequency == "month":
                print("month")
                total_value_of_days_left = (user_subscription.subscription_choice.price/30) * days_left
            elif user_subscription.subscription_choice.stripe_renewal_frequency == "year":
                print("year")
                total_value_of_days_left = (user_subscription.subscription_choice.price/365) * days_left

            print(total_value_of_days_left)
            if subscription_choice.stripe_renewal_frequency == "month":
                cost_per_day_new_plan = (subscription_choice.price/30)
            elif subscription_choice.stripe_renewal_frequency == "year":
                cost_per_day_new_plan = (subscription_choice.price/365)
            print(cost_per_day_new_plan)   
            days_left = int(total_value_of_days_left/cost_per_day_new_plan)
            context['remaining_days'] = True

        else:
            context['existing_higher_tier_subscription'] =True


        #round days down
        if days_left > 0:

            trial_period_days += days_left
        
    #Do the same for free trial days left
    # Need to convert? Decided not to convert and give user extra
    if user_payment_status.status == "free_trial":
        days_left = int((user_payment_status.subscription_expiry - current_time).days)
        if days_left > 0:
            trial_period_days += days_left
            context['remaining_days'] = True

    
    context['trial_period_days'] = trial_period_days


    try:
            # Create the subscription.
            # latest invoice and that invoice's payment_intent
            # so we can pass it to the front end to confirm the payment
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_id,
                }],
                trial_period_days= trial_period_days,
                # trial_end=1652631902,
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                # metadata={'page_id': page_id}
            )
            subscription_id = subscription.id

                
            if trial_period_days != 0:
                setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                usage = 'off_session'

                )
                client_secret = setup_intent.client_secret
            else:
                client_secret = subscription.latest_invoice.payment_intent.client_secret



    except Exception as e:
        print("Exception occured")
        print(e)

    return_url = request.build_absolute_uri(reverse('success', kwargs={'subscription_id': subscription_id}))


    #Created here so the stripe customer id is stored and not lost
    user_subscription = UserSubscriptions.objects.create(
        user_payment_status=user_payment_status,
        status = "created",
        stripe_customer_id = customer_id,
        subscription_id = subscription_id,
        next_due = datetime.utcfromtimestamp(subscription['current_period_end']),
        payment_method = "Stripe",
        amount_subscribed = price,
        renewal_frequency = subscription_choice.renewal_frequency,
        currency_code = currency_code,
        subscription_choice = subscription_choice,
    )



    event_unique_id =  uuid4()

    context['client_secret'] =  client_secret
    context['stripe_pub_key'] =  stripe_pub_key
    context['return_url'] =  return_url
    context['subscription_choice'] =  subscription_choice
    context['event_id'] =  event_unique_id
    context['trial_period_days'] =  trial_period_days
    context['user_subscription'] = user_subscription
    
    # context['user_pages'] = Page.objects.filter(user=user)


    print(context)
    
    return render(request, 'dashboard/htmx_elements/subscribe.html', context=context)




# Create your views here.

def _post_subscription_success(subscription_id=None, request=None, stripe_customer_id=None):
    print("POST SUBSCRIPTION SUCCESS")
    print(stripe_customer_id)
    context = {}

    if not stripe_customer_id:

        user_subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
        stripe_customer_id = user_subscription.stripe_customer_id
    else:
        user_subscription = UserSubscriptions.objects.get(stripe_customer_id=stripe_customer_id)
        

    subscriptions = stripe.Subscription.list(
     customer=stripe_customer_id,
    )
    print('post subscription success', )
    print(subscriptions)
    
    subscription_id = (subscriptions['data'][0]['id'])
    user_subscription.subscription_id = subscription_id
    user_subscription.save()
    
    print(subscriptions['data'][0]['items']['data'][0]['plan'])
    subscription_status_is_active = (subscriptions['data'][0]['items']['data'][0]['plan']['active'])
    print(subscription_status_is_active)

    if subscription_status_is_active == True:
        print("Active")
    
        next_payment_due = subscriptions['data'][0]['current_period_end']
        interval_start_date = subscriptions['data'][0]['current_period_start']

        
        #Use the subscription_id and customer_id to get the customer and the subscription
        user_subscription.status = "paid"
        user_subscription.next_due =  datetime.utcfromtimestamp(next_payment_due)
        user_subscription.latest_response = subscriptions
        user_subscription.interval_start_date = datetime.utcfromtimestamp(interval_start_date)
        user_subscription.save()

        #Update this
        user_payment_status = user_subscription.user_payment_status
        user_payment_status.status = "active"
        user_payment_status.subscription_expiry = user_subscription.next_due

        # update tier 

        # to handle downgrades  add a check for valid cancelled subscriptions
        # that are greater than current tier
        # if exists set tier to this
        try:
            user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                        user_payment_status=user_payment_status,
                        status="cancelled"),
                        next_due__gte= datetime.now(),
                        subscription_choice__tier__tier_ranking__gt=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                            'subscription_choice__tier__tier_ranking')).reverse()[0]

            if user_subscription_with_greater_tier.next_due.replace(tzinfo=None)  > datetime.now().replace(tzinfo=None):
                user_payment_status.tier = user_subscription_with_greater_tier.subscription_choice.tier
                user_payment_status.next_due = user_subscription_with_greater_tier.next_due
        except Exception as e:
            print(e)
            user_payment_status.tier = user_subscription.subscription_choice.tier
        user_payment_status.save()
        print('user_payment_status.tier', user_payment_status.tier)

        #Check and Modify any other values required

        # convert to model method?

    #-Send subscription confirmed email


    try: 
        
        subscription_confirmed_email.delay(subscription_id) 
        print("subscription confirm email scheduled")
    except Exception as e:
        print(e)


    #Get response and set to purchased (latest createUserPref)

    user = user_subscription.user_payment_status.user

    try:
        response = Response.objects.filter(user=user).latest('last_modified')
        response.purchased = True
        response.save()
        context['quiz'] = response.quiz

    except Response.DoesNotExist:
        print("no response found to set response.purchased to true")

    #Conversion tracking
    event_unique_id = uuid4()

    if request:
        event_source_url = request.META.get('HTTP_REFERER')

    else:
        event_source_url = request.build_absolute_uri(reverse('subscription_page_dashboard'))
    print("Source URL for product view")
    print(event_source_url)



    try:
        session = _session(request)
        conversion_tracking.delay(request=request, event_name="Subscribe", event_id=event_unique_id, event_source_url=event_source_url, category_id=context['quiz'].category.id, session_id=session.session_id)
        print("tracking conversion")
    
    except Exception as e:
        print("failed conv tracking")

        print(e)



    context = {
        'page_subscription': user_subscription,
        'event_id': event_unique_id,
       
        }



    return context


#payment success return_url uses this view
@login_required
def success(request, subscription_id):
    user = request.user
    user_subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
    if user == user_subscription.user_payment_status.user:
        context = _post_subscription_success(subscription_id=subscription_id, request=request)
    
    #Create template and render success
        # context['user_pages'] = Page.objects.filter(user=user)

        return render(request, 'dashboard/thankyou.html', context=context)
    return HttpResponse(300)


#Verify payment succeeded and create payment object
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

# Events triggered when subscribing with free trial
# setup_intent.succeeded
#Events without free trial
#payment_intent.succeeded

#Now need to get payment intent id from these events and trigger func below


    event_type = event['type']
    print('event_type', event_type)
    
    if event_type == 'setup_intent.succeeded':
        customer_id = event['data']['object']['customer']
        _post_subscription_success(stripe_customer_id=customer_id)
        print("EVENT SETUP INTENT WEBHOOK RECIEVED")
    
    elif event_type == 'payment_intent.succeeded':
        print('payment_intent.succeeded')
        customer_id = event['data']['object']['customer']
        _post_subscription_success(stripe_customer_id=customer_id)
    


    elif event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        pass

    elif event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        pass
    elif event_type == 'customer.subscription.deleted':
        pass
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.

    return HttpResponse(status=200)


def cancel_subscription(request):

    #For now cancel subscription then will have to modify subscribe function to take into
    # account current page expiry before charging use stripe.SubscriptionSchedule.create
    #This will then check for previsouly cancelled subscriptions for page
    #If found then use next due date as start date for next subscription


    #Also manage page susbcriptions should siplay previous subscriptions and their respective
    #invoices

    
    #Use the stripe method Cancel subscription at billing end
    user=request.user
    user_payment_status = UserPaymentStatus.objects.get(user=user)
    
    user_subscription = UserSubscriptions.objects.get(user_payment_status=user_payment_status, status="paid")


    stripe_subscription_id = user_subscription.subscription_id
    #Use the stripe method Cancel subscription at billing end
    
    try:
        stripe.Subscription.modify(
        stripe_subscription_id,
        cancel_at_period_end=True
        )

        #Thrn update all values
        user_subscription.status = "cancelled"
        user_subscription.save()

        messages.success(request, "Subscripton successfully cancelled")

        try:
            subscription_cancelled.delay(user_subscription.subscription_id)
        except Exception as b:
                print(b)

    except Exception as e:
        messages.error(request, "An error occured when cancelling the subscription")

        print(e)
    return redirect('subscription_page_dashboard')




  