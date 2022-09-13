

from django.shortcuts import render, redirect
from quiz_backend.models import Quiz
from blog.models import BlogPage

def home(request):
    quizes = Quiz.objects.all()

    context = {
        'quizes': quizes,
    }

    return render(request, 'home_site/index.html', context=context)

def robots_txt(request):
    return render(request, 'robots.txt')

# def about(request):
#     return render(request, 'home_site/pages/about.html')

# def contact(request):
#     return render(request, 'home_site/pages/contact.html')

def tandc(request):
    return render(request, 'home_site/pages/tandc.html')


def privpolicy(request):
    context = {
    }
    return render(request, 'home_site/pages/privpolicy.html', context=context)

def deliveryinfo(request):
    return render(request, 'home_site/pages/deliveryinfo.html')


def refundpolicy(request):
    return render(request, 'home_site/pages/refundpolicy.html')

def redirect_old_blog(request, slug):
    page = BlogPage.objects.get(slug=slug)
    
    return redirect(page.get_full_url(request=request))
