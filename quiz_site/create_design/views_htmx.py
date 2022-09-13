from django.shortcuts import render, HttpResponse

from create_design.forms import CreateDesignForm
from create_design.models import CreateDesignRequest
from quiz_backend.views import _session
from emails.models import UserEmail

def post_create_design(request):
    context = {}
    form = CreateDesignForm(request.POST)
    if form.is_valid():
        create_des_req = CreateDesignRequest()
        create_des_req.orientation = request.POST['orientation']
        create_des_req.image = form.cleaned_data('image')
        create_des_req.session = _session(request)
        create_des_req.status = "requested"
        
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

        #Npw need to call api (delay task and then change req status to true)

        return HttpResponse("SUccess")
    else:
        context['submitted'] = True
        context['form'] = form

    return render(request, "create_design/includes/create_design_form.html", context=context)