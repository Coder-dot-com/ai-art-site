from django.shortcuts import render,HttpResponse

from create_design.forms import CreateDesignForm

# Create your views here.

def create_design(request):
    context = {}
    context['form'] = CreateDesignForm
    
    return render(request, 'create_design/create_design.html', context=context)

def created_design_with_id(request, design_id):
    return HttpResponse(design_id)
    pass