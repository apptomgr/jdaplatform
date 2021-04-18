from django.urls import path
from . import views


urlpatterns = [
    path('', views.jdaanalyticsapp_home, name='jdaanalyticsapp_home')
]
