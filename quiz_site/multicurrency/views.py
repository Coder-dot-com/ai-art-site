from http.client import HTTPResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Currency
from quiz_backend.views import _session
# Create your views here.

def chosen_currency(request, currency_code):
    url = request.META.get('HTTP_REFERER')

    #1. Get chosen_currency 
    #2. Check when rate last updated and update asynchronously
    #2. Get session ID _cart_id
    #3. Set session currency to selected
    #4. Render/redirect to referrer or if not allowed referrer then to home page
    #5 Wherever there is a price i.e. in views it should check currency and convert and render currency
    
    #initially need to set up USD currency in
    session = _session(request)
    try: 
        currency_code = Currency.objects.get(currency_code=currency_code)
    except:
        return redirect(url) 
        
    try: 
        session.currency = currency_code
        session.save()     
    except Exception as e:
        print("error when setting currency", e)


    return redirect(url) 



def chosen_currency_subscription(request, currency_code):

    #1. Get chosen_currency 
    #2. Check when rate last updated and update asynchronously
    #2. Get session ID _cart_id
    #3. Set session currency to selected
    #4. Render/redirect to referrer or if not allowed referrer then to home page
    #5 Wherever there is a price i.e. in views it should check currency and convert and render currency
    
    #initially need to set up USD currency in
    session = _session(request)
    try: 
        currency_code = Currency.objects.get(currency_code=currency_code)
    except Exception as e:
        print("error when setting currency", e)
        return HTTPResponse(500)
        
    try: 
        session.currency = currency_code
        session.save()     
    except Exception as e:
        print("error when setting currency", e)
        return HTTPResponse(500)


    return redirect('subscription_component') 

