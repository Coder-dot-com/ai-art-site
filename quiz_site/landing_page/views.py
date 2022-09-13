from django.http import HttpResponse
from django.shortcuts import render

from emails.models import UserEmail
from common.util.functions import event_id
from conversion_tracking.tasks import conversion_tracking
from quiz_backend.models import Category

from .forms import EmailForm
from quiz_backend.views import _session

# Create your views here.

def launch_page(request):
    email_form = EmailForm()
    context = {
        'email_form': email_form
    }
    
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

    return render(request, 'landing_page/index.html', context=context)


def launch_page_signup(request):

    if request.POST:
        email_form = EmailForm(request.POST)
        context={}


        if email_form.is_valid():
            context['success'] = 'success'
            email = email_form.cleaned_data.get('email')
            # Here create email object
            UserEmail.objects.create(email=email, promo_consent=True)
            session = _session(request)
            session.email = email
            session.save()
                #/conv tracking
            #Add custom event html snippet
    
            event_source_url = request.META.get('HTTP_REFERER')


            lead_event_id = event_id()
            context['lead_event_id'] = lead_event_id
            print("lead")
            category = Category.objects.all()[0]
            context['category'] = category
            conversion_tracking.delay(event_name="Lead", event_id=lead_event_id, event_source_url=event_source_url, category_id=category.id, session_id=session.session_id)  


        else:
            for field in email_form.errors:
                email_form[field].field.widget.attrs['class'] += ' is-invalid'

        context['email_form'] = email_form

        return render(request, 'landing_page/htmx_signup.html', context=context)

        
    else:
        pass