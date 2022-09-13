"""mem_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views, views_htmx

urlpatterns = [
    path('', views.dashboard_home, name="dashboard_home",),
    path('subscribe/', views.subscription_page_dashboard, name="subscription_page_dashboard"),
    path('account_details/', views.account_details_dashboard, name="account_details_dashboard"),
    path('change_password/', views.change_password_dashboard, name="change_password_dashboard"),
    path('billing_history/', views.billing_history, name="billing_history"),
    path('preferences/', views.dashboard_preferences, name="dashboard_preferences"),
    path('subscription_component/', views_htmx.subscription_component, name="subscription_component"),

]
