from django.urls.conf import path
from . import views

urlpatterns = [
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
]