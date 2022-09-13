from datetime import datetime
from quiz_backend.views import _session
from django.shortcuts import render

from subscriptions.models import SubscriptionChoices, UserPaymentStatus, UserSubscriptions
from django.db.models import Q
from django.db.models import Max

def subscription_component(request):
    print("subscription component")
    session = _session(request)
    context = {}
    # context['user_pages'] = Page.objects.filter(user=request.user)

    if request.user.is_authenticated:
        user=request.user
        user_payment_status = UserPaymentStatus.objects.get(user=user)

        if user_payment_status.status == "active":
            try:
                user_subscription = UserSubscriptions.objects.filter(
                    user_payment_status=user_payment_status,
                    status="paid", 

                    ).latest('created_at')
            except UserSubscriptions.DoesNotExist:
                try:
                    user_subscription = UserSubscriptions.objects.filter(
                user_payment_status=user_payment_status,
                status="cancelled", 
                ).latest('created_at')
                except:
                    user_subscription = ""
            context['user_subscription'] = user_subscription

            try:
                user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                        user_payment_status=user_payment_status,
                        status="cancelled"),
                        next_due__gte= datetime.now(),
                        subscription_choice__tier__tier_ranking__gt=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                            'subscription_choice__tier__tier_ranking')).reverse()[0]


                if user_subscription_with_greater_tier.next_due.replace(tzinfo=None)  > datetime.now().replace(tzinfo=None):
                    context['previous_cancelled_subscription'] = user_subscription_with_greater_tier

            except Exception:
                pass
    #Rendering based on annual or monnthly

    subscription_choices = SubscriptionChoices.objects.filter(currency__currency_code=session.currency.currency_code, renewal_frequency="annually")
    context['annual'] = True

    if (request.method == "POST"):
        try:
            annual = request.POST['interval']
        except:
            subscription_choices = SubscriptionChoices.objects.filter(currency__currency_code=session.currency.currency_code, renewal_frequency="monthly")
            context['annual'] = False


    context['subscription_choices'] = subscription_choices

    return render(request, 'dashboard/components/htmx/subscription_choices_htmx.html', context=context)
