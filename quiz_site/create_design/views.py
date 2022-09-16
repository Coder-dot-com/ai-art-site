from django.shortcuts import render,HttpResponse

from create_design.forms import BuyForm, CreateDesignForm
from create_design_buy.utils.payment_success import post_payment_success
from .models import CreateDesignRequest
import stripe
from quiz_site.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

# Create your views here.

def create_design(request):
    context = {}
    context['form'] = CreateDesignForm()
    
    return render(request, 'create_design/create_design.html', context=context)

def created_design_with_id(request, design_id):
    context = {}
    context['form'] = CreateDesignForm()
    context['created_design'] = CreateDesignRequest.objects.get(unique_id=design_id)
    context['buy_form'] = BuyForm(initial={'design_id': design_id})

    #check if stripe payment succeeded
    print('request', request)
    try:
        payment_intent = request.GET['payment_intent']
    except:
        payment_intent = None
        
    if payment_intent:
        #Use payment intent to check if payment was successful, get list of charges
        intent = stripe.PaymentIntent.retrieve(payment_intent)
        charges = intent.charges.data
        for charge in charges:
            if (charge['paid']) == True:
                context['successful_payment'] = True
            # call post succcess func
                post_payment_success(payment_intent)

    return render(request, 'create_design/create_design.html', context=context)
