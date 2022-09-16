import time
from django.shortcuts import render, HttpResponse

from create_design.forms import BuyForm, CreateDesignForm
from create_design.models import BuyOptions, CreateDesignRequest
from quiz_backend.views import _session
from emails.models import UserEmail
import requests

from create_design.tasks import create_design_task

def post_create_design(request):
    context = {}
    form = CreateDesignForm(request.POST, request.FILES)
    if form.is_valid():
        create_des_req = CreateDesignRequest()
        create_des_req.orientation = request.POST['orientation']
        create_des_req.image = form.cleaned_data.get('image')
        create_des_req.session = _session(request)
        create_des_req.status = "requested"
        create_des_req.effect = form.cleaned_data.get('effect')

        email = form.cleaned_data.get('email')
        email_consent = form.cleaned_data.get('email_consent')
        try:
            email_obj = UserEmail.objects.get(email=email)
            email_obj.promo_consent = email_consent
            email_obj.save()
        except UserEmail.DoesNotExist:
            email_obj = UserEmail.objects.create(email=email, promo_consent=email_consent)
        except Exception as e:
            print(e)

        create_des_req.email = email_obj
        create_des_req.save()


        # create_design_task.delay(create_des_req.id)
        context['form'] = CreateDesignForm()
        context['success'] = True


        return render(request, 'create_design/includes/create_design_form.html', context=context)
    else:
        context['submitted'] = True
        context['form'] = form

    return render(request, "create_design/includes/create_design_form.html", context=context)


def created_design_loader(request):
    session = _session(request)
    created_design = CreateDesignRequest.objects.filter(session=session).latest('date_of_request')
    context = {}
    context['unique_id'] = created_design.unique_id
    return render(request, 'create_design/includes/success_loader.html', context=context)

def created_design(request):
    session = _session(request)

    created_design = CreateDesignRequest.objects.filter(session=session).latest('date_of_request')
    attempts = 1

    print(created_design.id, "crid")

    while attempts < 40 and not created_design.design_preview:
        created_design = CreateDesignRequest.objects.filter(session=session).latest('date_of_request')
        attempts += 1
        time.sleep(2)

    
    if not created_design.design_preview:
        return HttpResponse(f"<center><b>Error occured, please contact us with this id: {session.session_id}</b></center>")

    context = {}
    context['created_design'] = created_design
    context['buy_form'] = BuyForm(initial={'design_id': created_design.unique_id})
    return render(request, 'create_design/includes/design_display.html', context=context)


def size_select_options(request, design_id):
    context= {}
    created_design = CreateDesignRequest.objects.get(unique_id=design_id)
    type_chosen = dict(request.POST)['type'][0]
    print(type_chosen)
    if not type_chosen == 'Digital':
        context['size_options'] = BuyOptions.objects.filter(orientation=created_design.orientation, 
        type_of_purchase=type_chosen)

    else:
        context['size_options'] = BuyOptions.objects.filter(type_of_purchase=type_chosen)
        context['digital'] = True
    return render(request, 'create_design/htmx_elements/size_select.html', context=context)