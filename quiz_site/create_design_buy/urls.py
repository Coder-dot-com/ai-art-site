from django.urls.conf import path
from . import views, views_htmx

urlpatterns = [
    path('shipping_form_and_options/<order_number>/', views_htmx.shipping_form_and_options, name="shipping_form_and_options"),
    path('submit_buy_form/', views_htmx.submit_buy_form, name="submit_buy_form"),
    path('submit_shipping_form/', views_htmx.submit_shipping_form, name="submit_shipping_form"),
    

]