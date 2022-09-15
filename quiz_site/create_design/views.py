from django.shortcuts import render,HttpResponse

from create_design.forms import BuyForm, CreateDesignForm
from .models import CreateDesignRequest

# Create your views here.

def create_design(request):
    context = {}
    context['form'] = CreateDesignForm()
    
    return render(request, 'create_design/create_design.html', context=context)

def created_design_with_id(request, design_id):
    context = {}
    context['form'] = CreateDesignForm()
    context['created_design'] = CreateDesignRequest.objects.get(unique_id=design_id)
    context['buy_form'] = BuyForm()

    return render(request, 'create_design/create_design.html', context=context)
