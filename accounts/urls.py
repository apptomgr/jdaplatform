from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('register/', views.register, name='register'),
    # path('register/', views.signup, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/',views.profile, name='profile'),
    path('profile_edit/',views.profile_edit, name='profile_edit'),
    path('account_admin/',views.account_admin, name='account_admin'),
    path('account_admin_update/',views.account_admin_update, name='account_admin_update'),

]
