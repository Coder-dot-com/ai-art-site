from django.urls import path
from . import views


urlpatterns = [
    path('<currency_code>', views.chosen_currency, name='chosen_currency'),
    path('chosen_currency_subscription/<currency_code>', views.chosen_currency_subscription, name='chosen_currency_subscription'),

] 