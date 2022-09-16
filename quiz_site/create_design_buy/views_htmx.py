import datetime
from wsgiref.util import request_uri
from django.shortcuts import render, HttpResponse, redirect 
from django.urls import reverse
from create_design.forms import BuyForm
from create_design.models import BuyOptions, CreateDesignRequest
from emails.models import UserEmail
from create_design_buy.models import Order, OrderProduct
from quiz_backend.views import _session
import stripe
from .forms import ShippingForm
from quiz_site.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
# Create your views here.


stripe.api_key = STRIPE_SECRET_KEY
stripe_pub_key = STRIPE_PUBLIC_KEY

def shipping_form_and_options(request, order_number):
    context = {}
    context['shipping_form'] = ShippingForm(initial={'order_number': order_number,})
    return render(request, 'create_design/includes/shipping_form.html', context=context)

def submit_shipping_form(request):
    context = {}
    user_session = _session(request)
    form = ShippingForm(request.POST)
    if form.is_valid():
        order_number = form.cleaned_data.get('order_number')
        order = Order.objects.get(session=user_session, order_number=order_number)
        #Updat order with details

        order.ship_first_name = form.cleaned_data.get('first_name')
        order.ship_last_name = form.cleaned_data.get('last_name')
        order.ship_address_line_1 = form.cleaned_data.get('address_line_1')
        order.ship_address_line_2 = form.cleaned_data.get('address_line_2')
        order.ship_country = form.cleaned_data.get('country')
        order.ship_state = form.cleaned_data.get('state_county')
        order.ship_city = form.cleaned_data.get('city')
        order.ship_postcode = form.cleaned_data.get('postcode_zip')




        currency = user_session.currency
        currency.check_to_update_rate()

        #Convert only for item with quantity 1 for now
        # (same as submit buy form)
        # Todo for multi quantity/products convert then multiple by quantity then 
        # for loop over order products (change get to filter)   for the total     
        order_product = OrderProduct.objects.get(order=order)
        purchase_option = order_product.product

        converted_amount = currency.usd_to_currency_rounded(purchase_option.price)
        order.order_subtotal = converted_amount
        order.currency = currency
        order.one_usd_to_currency_conv_rate_when_placed= currency.one_usd_to_currency_rate

        shipping_method = form.cleaned_data.get('shipping')
        order.shipping_method = shipping_method.option

        #Convert the shipping method price
        converted_shipping_price = currency.usd_to_currency_rounded(shipping_method.price)
        order.shipping_price = converted_shipping_price
        #Calculate order total and set along with currency
        order_total = converted_shipping_price + converted_amount
        order.order_total = order_total
        order.save()

        intent = stripe.PaymentIntent.create(
        amount = int(order_total*100),
            currency = currency,
            payment_method_types = [
                "card",
            ],
            )
        payment_intent_id = intent.id
        order.payment_intent_id = payment_intent_id
        order.save()

        #Render stripe checkout and add payment intent to order

        context = {}
        context['stripe_pub_key'] = STRIPE_PUBLIC_KEY
        context['client_secret'] = intent.client_secret
        return_url = request.build_absolute_uri(reverse('created_design_with_id', kwargs={"design_id": order_product.design_request.unique_id}
        ))
        context['return_url'] = f"""{return_url}?pi={payment_intent_id}"""


        return render(request, 'create_design_buy/stripe_payment_element.html', context=context)
    
    context['shipping_form'] = form
    context['submitted'] = True
    return render(request, 'create_design/includes/shipping_form.html', context=context)


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


