from django.shortcuts import render,HttpResponse

from create_design.forms import BuyForm, CreateDesignForm, EffectPreviewForm
from create_design_buy.utils.payment_success import post_payment_success
from create_design_buy.models import Order
from common.util.functions import event_id
from quiz_backend.models import Category
from conversion_tracking.tasks import conversion_tracking
from .models import CreateDesignRequest, Effect
import stripe
from quiz_site.settings import STRIPE_SECRET_KEY
from quiz_backend.views import _session

stripe.api_key = STRIPE_SECRET_KEY

# Create your views here.

def create_design(request):
    context = {}
    context['form'] = CreateDesignForm()
    context['preview_form'] = EffectPreviewForm(initial={'effect': 1})
    context['effects'] = Effect.objects.all().filter(active=True)

    pv_event_unique_id = event_id()
    vc_event_unique_id = event_id()
    context['pv_event_unique_id'] = pv_event_unique_id
    context['vc_event_unique_id'] = vc_event_unique_id
    # context['vcfs_event_unique_id'] = vcfs_event_unique_id

    event_source_url = request.META.get('HTTP_REFERER')

    session = _session(request)
    category = Category.objects.all()[0]

    try:
        # Need to fix this to ensure different ids
        conversion_tracking.delay(event_name="PageView", event_id=pv_event_unique_id, event_source_url=event_source_url, category_id=category.id, session_id=session.session_id)  
        conversion_tracking.delay(event_name="ViewContent", event_id=vc_event_unique_id, event_source_url=event_source_url, category_id=category.id, session_id=session.session_id)  
        # conversion_tracking.delay(event_name="ViewContentFromShare", event_id=vcfs_event_unique_id, event_source_url=event_source_url, category_id=quiz.category.id, session_id=session.session_id)  

        print("tracking conversion")
    except Exception as e:
        print("failed conv tracking")

        print(e)

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
                context['order'] = Order.objects.get(payment_intent_id=payment_intent)

    return render(request, 'create_design/create_design.html', context=context)
