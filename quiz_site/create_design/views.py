from django.shortcuts import render

from create_design.forms import CreateDesignForm

# Create your views here.

def create_design(request):
    context = {}
    context['form'] = CreateDesignForm
    
    return render(request, 'create_design/create_design.html', context=context)