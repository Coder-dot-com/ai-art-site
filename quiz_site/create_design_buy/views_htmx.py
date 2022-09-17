import datetime
from enum import unique
from wsgiref.util import request_uri
from django.shortcuts import render, HttpResponse, redirect 
from django.urls import reverse
from create_design.forms import BuyForm
from create_design.models import BuyOptions, CreateDesignRequest
from emails.models import UserEmail
from create_design_buy.models import Order, OrderProduct, ShippingOption
from quiz_backend.views import _session
import stripe
from .forms import ShippingForm
from quiz_site.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
# Create your views here.


stripe.api_key = STRIPE_SECRET_KEY
stripe_pub_key = STRIPE_PUBLIC_KEY

def buy_now_form_options(request, unique_id):
    created_design = CreateDesignRequest.objects.get(unique_id=unique_id)
    context = {}
    context['created_design'] = created_design
    context['buy_form'] = BuyForm(initial={'design_id': created_design.unique_id})
    return render(request, 'create_design/includes/buy_now_form.html', context=context)

def shipping_form_and_options(request, order_number):
    context = {}

    #For form check if existing details for order, then set to them
    try:
        order = Order.objects.get(order_number=order_number)
    except:
        order = None

    if order:
        context['shipping_form'] = ShippingForm(initial={
            'order_number': order_number,
            'shipping': order.shipping_foreignkey,
            'first_name': order.ship_first_name,
            'last_name': order.ship_last_name,
            'address_line_1': order.ship_address_line_1,
            'address_line_2': order.ship_address_line_2,
            'country': order.ship_country,
            'state_county': order.ship_state,
            'city': order.ship_city,
            'postcode_zip': order.ship_postcode,
            })
    else:
        context['shipping_form'] = ShippingForm(initial={'order_number': order_number,})


    # Later use filter?
    context['order_product'] = OrderProduct.objects.get(order__order_number=order_number)
    return render(request, 'create_design/includes/shipping_form.html', context=context)

def shipping_options(request, order_number):
    context = {}
    context['shipping_options'] = ShippingOption.objects.all()
    return render(request, 'create_design/htmx_elements/shipping_select.html', context=context)

def submit_shipping_form(request, order_number):
    context = {}
    user_session = _session(request)
    form = ShippingForm(request.POST)
    order = Order.objects.get(session=user_session, order_number=order_number)
    #Convert only for item with quantity 1 for now
    # (same as submit buy form)
    # Todo for multi quantity/products convert then multiple by quantity then 
    # for loop over order products (change get to filter)   for the total     
    order_product = OrderProduct.objects.get(order=order)
    
    if form.is_valid() or order_product.product.type_of_purchase == 'Digital':
            # If order_product digital skip to checkout


        #Updat order with details
        if form.is_valid():
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

        purchase_option = order_product.product

        converted_amount = currency.usd_to_currency_rounded(purchase_option.price)
        order.order_subtotal = converted_amount
        order.currency = currency
        order.one_usd_to_currency_conv_rate_when_placed= currency.one_usd_to_currency_rate
        if not order_product.product.type_of_purchase == 'Digital':
            shipping_method = form.cleaned_data.get('shipping')
            order.shipping_method = shipping_method.option
            order.shipping_foreignkey = shipping_method
        #Convert the shipping method price
            converted_shipping_price = currency.usd_to_currency_rounded(shipping_method.price)
            order.shipping_price = converted_shipping_price
        #Calculate order total and set along with currency
            order_total = converted_shipping_price + converted_amount
        else:
            order_total = converted_amount
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
        context['order']  = order
        context['order_product'] = order_product

        return render(request, 'create_design_buy/stripe_payment_element.html', context=context)
    
    context['shipping_form'] = form
    context['submitted'] = True
    context['order_product'] = order_product



    return render(request, 'create_design/includes/shipping_form.html', context=context)




def submit_buy_form(request, order_num=False):
    print(request.POST)
    user_session = _session(request)
    design_id = dict(request.POST)['design_id'][0]
    created_design = CreateDesignRequest.objects.get(unique_id=design_id)
    form = BuyForm(request.POST)
    if form.is_valid():
        #Create email object
        email = form.cleaned_data.get('email')
        email_consent = form.cleaned_data.get('email_consent')

        if  order_num:

            order = Order.objects.get(order_number=order_num)
            
            email_obj = order.email
            if email_obj:
                email_obj.delete()
        else:
            order = Order()

        try:
                email_obj = UserEmail.objects.get(email=email)
                email_obj.promo_consent = email_consent
                email_obj.save()
        except UserEmail.DoesNotExist:
                email_obj = UserEmail.objects.create(email=email, promo_consent=email_consent)
            # Create the order object


        order.session = user_session
            #Get the product, currency of user and converted amount for order total
        if not form.cleaned_data.get('type') == 'Digital':
            purchase_option = BuyOptions.objects.get(orientation=created_design.orientation, type_of_purchase=form.cleaned_data.get('type'), size=request.POST.get('size'))
        else:
            purchase_option = BuyOptions.objects.get( type_of_purchase=form.cleaned_data.get('type'))
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

        if not order_num:
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")

            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            
        #Create Order Product object
        OrderProduct.objects.filter(order=order).delete()
        
        OrderProduct.objects.create(order=order, product=purchase_option, design_request=created_design,
        quantity=1)
    
        return redirect('shipping_form_and_options', order_number = order.order_number)
    else:
        context = {}
        context['created_design'] = created_design
        context['buy_form'] = form
        context['submitted'] = True
        return render(request, 'create_design/includes/buy_now_form.html', context=context)


def edit_size_select_buy_form(request, design_id):

    #Pass initial values
    #Then also edit submit to take an optional order id,
    #If order id then checks and updates (with email laso update on SIB)
    created_design = CreateDesignRequest.objects.get(unique_id=design_id)
    order_product = OrderProduct.objects.filter(order__status='created',
     order__session=_session(request), design_request=created_design
    ).latest('order__modified')
    
    product = order_product.product

    order = order_product.order

    #Need purchase option, size, email, email_consent
    form = BuyForm(initial ={'type': product.type_of_purchase, 'design_id': design_id,
     'email': order.email.email,
     'promo_consent': order.email.promo_consent,
     })
    context = {}
    context['created_design'] = created_design
    context['buy_form'] = form
    context['order_number'] = order_product.order.order_number
    return render(request, 'create_design/includes/buy_now_form.html', context=context)
