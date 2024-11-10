
from django.urls import path
from .views import index, ajax_view

urlpatterns = [
    path('', index),
    path('your-django-url/', ajax_view, name='ajax_view'),

]
