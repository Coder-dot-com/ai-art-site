from .models import Currency
from  quiz_backend.views import _session
import requests
from decouple import config

def currency(request):
    try:
        currencies = Currency.objects.all()
    except:
        currency = None

    return dict(currencies=currencies)

def user_current_currency(request):
    #initially need to set up USD currency in admin
    session = _session(request)

    if session.currency:
        session_currency = session.currency
        pass
        #Try to get exisisting currnecy 
    else:
        #If fails then now need to auto detect correct currency
            #Add autodetect logic here~
            print("User ip is ")
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            print(ip)

            if request.method == 'GET' and ip !="127.0.0.1":

                IP_API_KEY = config('IP_API_KEY')
                response = requests.get(f'https://ipapi.co/{str(ip)}/json/?key={IP_API_KEY}').json()
                print(response)
                user_currency = response.get("currency")
                country_code = (str(response.get("country_code"))).lower()

                print("auto detected currency is:")
                print(user_currency)
                print("country code is")
                print(country_code)

                session.country_code = country_code
                session.save()
                
                try:
                
                    user_currency = Currency.objects.get(currency_code=user_currency)
                    session.currency = user_currency
                    session.save()

                    session_currency = session.currency
                
                except:

                    try:

                        session.currency = Currency.objects.get(currency_code="USD")
                        session.save()
                        session_currency = session.currency
                
                
                    except Exception as e:
                        print("An exception occured when autodetecting currency")
                        print(e)
                        print("Attempting to assign USD as currency")


                        session_currency = "USD"
                

            
            else:
                try:
                    session.currency = Currency.objects.get(currency_code="USD")
                    session.save()
                

                    session_currency = session.currency
            
                except Currency.DoesNotExist:
                    session.currency = Currency.objects.create(currency_code="USD",
                    currency_display_name="USD",
                    currency_symbol="$",
                    )
                    session.save()
                

                    session_currency = session.currency                   



    print("session_currency", session_currency)

    
    #try if not then usd (try to create usd object)
    #If not then just return currency as usd

    return dict(session=session)