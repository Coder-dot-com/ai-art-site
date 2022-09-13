from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from quiz_site import settings
from . import views

urlpatterns = [
    path('subscribe/<int:option_id>/', views.stripe_payment_subscibe, name="stripe_payment_subscibe",),
    path('thankyou/<subscription_id>/', views.success, name='success'), 
    path('cancel-subscription/', views.cancel_subscription, name='cancel_subscription'), 
    path('webhook/', views.stripe_webhook, name="stripe_webhook")

]
