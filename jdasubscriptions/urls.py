# from django.urls import path
# from . import views
# from .views_admin import subscription_dashboard
#
# app_name = "jdasubscriptions"
#
# urlpatterns = [
#     path("subscription_plan_list/", views.subscription_plan_list, name="subscription_plan_list"),
#
#     path("select_subscription_plan/<int:plan_id>/", views.select_subscription_plan, name="select_subscription_plan"),
#     path("subscription_confirm/", views.subscription_confirm, name="subscription_confirm"),
#     path("institution_subscription_confirm/", views.institution_subscription_confirm, name="institution_subscription_confirm"),
#     ##views_admin
#     path("admin/dashboard/",subscription_dashboard, name="subscription_dashboard",),
#
#
# ]


from django.urls import path
from . import views
from .views_admin import subscription_dashboard

app_name = "jdasubscriptions"

urlpatterns = [
    path("plans/", views.subscription_plan_list, name="subscription_plan_list"),
    path("select/<int:plan_id>/", views.select_subscription_plan, name="select_subscription_plan"),
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"),
    path("success/", views.subscription_success, name="subscription_success"),
    path("failed/", views.subscription_failed, name="subscription_failed",),
    # jdasubscriptions/urls.py

    path("upgrade/",views.subscription_upgrade, name="subscription_upgrade",),


    ##views_admin
    path("admin/dashboard/",subscription_dashboard, name="subscription_dashboard",),
]




# from django.urls import path
# from . import views
#
# app_name = "jdasubscriptions"
#
# urlpatterns = [
#     path("", views.res, name="res"),
#     path("plans/", views.subscription_plan_list, name="subscription_plan_list"),
#     path("select/<int:plan_id>/", views.select_subscription_plan, name="select_subscription_plan"),
#     path("confirm/", views.subscription_confirm, name="subscription_confirm"),  # added for next step
# ]
