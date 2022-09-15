import datetime
from django.shortcuts import render, HttpResponse, redirect

from create_design.forms import BuyForm
from create_design.models import BuyOptions, CreateDesignRequest
from emails.models import UserEmail
from create_design_buy.models import Order, OrderProduct
from quiz_backend.views import _session
import stripe
from quiz_site.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
# Create your views here.


stripe.api_key = STRIPE_SECRET_KEY
stripe_pub_key = STRIPE_PUBLIC_KEY

def shipping_form_and_options(request, order_number):
    return HttpResponse(f"SHipping {order_number}")

def submit_buy_form(request):
    print(request.POST)
    user_session = _session(request)
    design_id = dict(request.POST)['design_id'][0]
    created_design = CreateDesignRequest.objects.get(unique_id=design_id)
    form = BuyForm(request.POST)
    if form.is_valid():
        #Create email object
        email = form.cleaned_data.get('email')
        email_consent = form.cleaned_data.get('email_consent')
        try:
            email_obj = UserEmail.objects.get(email=email)
            email_obj.promo_consent = email_consent
            email_obj.save()
        except UserEmail.DoesNotExist:
            email_obj = UserEmail.objects.create(email=email, promo_consent=email_consent)

        # Create the order object
        order = Order()
        order.session = user_session
            #Get the product, currency of user and converted amount for order total
        purchase_option = BuyOptions.objects.get(orientation=created_design.orientation, type_of_purchase=form.cleaned_data.get('type'), size=request.POST.get('size'))
        currency = user_session.currency
        currency.check_to_update_rate()
        converted_amount = currency.usd_to_currency_rounded(purchase_option.price)
        order.order_subtotal = converted_amount
        order.currency = currency
        order.one_usd_to_currency_conv_rate_when_placed= currency.one_usd_to_currency_rate


        order.email = email_obj
        order.status = "created"




        # order number
        order.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")

        order_number = current_date + str(order.id)
        order.order_number = order_number
        order.save()
            
        #Create Order Product object

        
        OrderProduct.objects.create(order=order, product=purchase_option, design_request=created_design,
        quantity=1)
    
        
        return redirect('shipping_form_and_options', order_number = order.order_number)
    else:
        context = {}
        context['created_design'] = created_design
        context['buy_form'] = form
        context['submitted'] = True
        return render(request, 'create_design/includes/buy_now_form.html', context=context)

