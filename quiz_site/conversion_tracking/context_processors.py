from quiz_backend.views import _session
import time

from conversion_tracking.models import ConversionExclusionsList
from quiz_backend.models import Referrer, UserSession


def get_and_set_session_values(request):
    session = _session(request)

    try:
            ip = None
                    
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
        
        
            session.ip = ip
    except Exception as e:
        print("failed to set ip for user", e)


    try:
            user_agent = request.META['HTTP_USER_AGENT']

            session.user_agent = user_agent


    except Exception as e:
        print("failed to set user agent for user", e)


    try:
        
            fbp = request.COOKIES['_fbp']
            session.latest_fbp = fbp


    except Exception as e:
        print("failed to set fbp for user", e)
    

    try:
        unix_time = int(time.time())      
        latest_fb_clid = f"fb.1.{unix_time}.{request.GET['fbclid']}"
        session.latest_fb_clid = latest_fb_clid

    except Exception as e:
        print("failed to set fbclid for user", e)
    
    

    try:
        referrer = (request.GET['ref'])
    except:
        referrer = "organic"        
    try:
        audience = request.GET['a1']
    except:
        audience = None
    try:
        ad = request.GET['ad2']
    except:
        ad = None

    try:
        latest_referrer = Referrer.objects.filter(user_session=session).latest('time_created')
    except:
        latest_referrer = None
        
    if (not latest_referrer or latest_referrer.referrer != referrer
    or latest_referrer.audience != audience or latest_referrer.ad !=ad):

        latest_referrer = Referrer.objects.create(user_session=session,
         referrer=referrer, audience=audience, ad=ad)

    # Modify admin display
    # Check for any errors/test
    try:    
        pass
    except Exception as e:
        print("failed to set  for user", e)
    
    session.save()
    enable_pixels_for_user = True

    try:
    
        if user_agent == 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0':
            enable_pixels_for_user = False

        elif ConversionExclusionsList.objects.filter(user_agent=user_agent):
            enable_pixels_for_user = False
        elif ConversionExclusionsList.objects.filter(ip=ip):
            enable_pixels_for_user = False
        elif '.html' in user_agent:
            enable_pixels_for_user = False
        
        elif UserSession.objects.filter(user_agent=user_agent,add_user_agent_to_exclusion_list=True):
            enable_pixels_for_user = False
                
    except Exception as e:
        print(e)
       



    return dict(values_set=True, enable_pixels_for_user = enable_pixels_for_user)

