from django.urls.conf import path
from . import views, views_htmx

urlpatterns = [
    path('', views.create_design, name="create_design"),
    path('post/', views_htmx.post_create_design, name="post_create_design"),

]