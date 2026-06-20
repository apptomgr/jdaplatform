from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

urlpatterns = [

    path('register/', views.register, name='register'),
    # path('register/', views.signup, name='register'),
    path('login/', auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('check-verification/', views.check_verification, name='check_verification'),
    path('profile/',views.profile, name='profile'),
    path('profile_edit/',views.profile_edit, name='profile_edit'),
    path('account_admin/',views.account_admin, name='account_admin'),
    path('account_admin_update/',views.account_admin_update, name='account_admin_update'),

    path('admin_tasks/',views.admin_tasks, name='admin_tasks'),
    path('admin_tasks_edit/<str:req_type>/<int:pk>',views.admin_tasks_edit, name='admin_tasks_edit'),
    path('admin_tasks_add',views.admin_tasks_add, name='admin_tasks_add'),
    path('admin_tasks_stats/<str:stats_type>',views.admin_tasks_stats, name='admin_tasks_stats'),

    #path('subscribe/', views.subscription_plans, name='subscription-plans'),
    #path("subscription/toggle/", views.subscription_type_toggle, name="subscription_type_toggle"),

    #path('checkout/summary/', views.subscription_checkout_summary, name='subscription_checkout_summary'),
    #path('checkout/auth-panel/', views.subscription_auth_panel, name='subscription_auth_panel'),



]
