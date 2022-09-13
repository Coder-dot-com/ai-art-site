from django.urls.conf import path
from . import views

urlpatterns = [
    path('postfbpdata', views.receive_fbp_post, name="postfbpdata"),

]