from django.urls.conf import path
from . import views

urlpatterns = [
    path('launch_page/', views.launch_page, name="launch_page"),
    path('launch_page_signup/', views.launch_page_signup, name="launch_page_signup"),

]