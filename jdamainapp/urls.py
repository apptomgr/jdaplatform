from django.urls import path
from . import views


urlpatterns = [
    path('', views.jdamainapp_home, name='jdamainapp_home')
]
