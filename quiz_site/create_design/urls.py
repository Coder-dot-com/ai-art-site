from django.urls.conf import path
from . import views, views_htmx

urlpatterns = [
    path('', views.create_design, name="create_design"),
    path('post/', views_htmx.post_create_design, name="post_create_design"),
    path('created_design_loader/', views_htmx.created_design_loader, name="created_design_loader"),
    path('created_design_with_id/<design_id>/', views.created_design_with_id, name="created_design_with_id"),
    path('created_design/', views_htmx.created_design, name="created_design"),
    path('size_select_options/<design_id>/', views_htmx.size_select_options, name="size_select_options"),
    path('create_design_form/', views_htmx.create_design_form, name="create_design_form"),

]