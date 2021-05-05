
from django.urls import path
from . import views

urlpatterns = [
    path('', views.jdawebsite_home, name='jdawebsite_home'),

]