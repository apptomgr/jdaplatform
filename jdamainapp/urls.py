from django.urls import path
from . import views


urlpatterns = [
    path('', views.jdamainapp_home, name='jdamainapp_home'),
    path('switch-language/', views.switch_language, name='switch_language'),
]
