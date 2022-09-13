
from django.contrib import admin
from django.urls import include, path
from . import views, views_htmx

urlpatterns = [
    path('<unique_id>/', views.quiz, name="quiz"),
    path('<unique_id>/submit_form/<response_id>/', views.submit_form, name="submit_form"),
    path('<unique_id>/submit_form/<response_id>/<ajax>/', views.submit_form, name="submit_form"),
    path('<unique_id>/termsandconditions/', views.tandc, name='tandc'), 
    path('<unique_id>/privacypolicy/', views.privpolicy, name='privpolicy'), 
    path('<unique_id>/deliveryinfo/', views.deliveryinfo, name='deliveryinfo'), 
    path('<unique_id>/refundpolicy/', views.refundpolicy, name='refundpolicy'), 
    path('<unique_id>/checkout/<response_id>', views.checkout, name='checkout'), 
    path('<unique_id>/upload_image/<response_id>/', views_htmx.image_upload, name="image_upload"),
    path('<unique_id>/upload_image/<response_id>/<user_image_id>/', views_htmx.delete_image, name="delete_image"),


]
