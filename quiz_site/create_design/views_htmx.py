from django.shortcuts import render, HttpResponse

from create_design.forms import CreateDesignForm

def post_create_design(request):
    context = {}
    form = CreateDesignForm(request.POST)
    if form.is_valid():
        #Start creating design

        #Create email object
        #Return spinner with loading that is pinging/checking for completion
        return HttpResponse("SUccess")
    else:
        context['submitted'] = True
        context['form'] = form

    return render(request, "create_design/includes/create_design_form.html", context=context)