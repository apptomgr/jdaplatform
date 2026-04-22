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
from . import views_admin

app_name = "jdasubscriptions"

urlpatterns = [
    path("api/public/subscription-plans/", views.public_subscription_plans, name="public_subscription_plans"),
    path("plans/", views.subscription_plan_list, name="subscription_plan_list"),
    path("select/<int:plan_id>/", views.select_subscription_plan, name="select_subscription_plan"),
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"),
    path("success/", views.subscription_success, name="subscription_success"),
    path("failed/", views.subscription_failed, name="subscription_failed",),
    path("upgrade/", views.subscription_upgrade, name="subscription_upgrade",),

    # Existing admin dashboard (KPIs / MRR)
    path("admin/dashboard/", views_admin.subscription_dashboard, name="subscription_dashboard",),

    # Subscriber reporting dashboard
    path("sub_dashboard/", views_admin.sub_dashboard, name="sub_dashboard"),
    path("sub_dashboard/expire/", views_admin.expire_subscription, name="expire_subscription"),
    path("sub_dashboard/extend/", views_admin.extend_subscription, name="extend_subscription"),
    path("sub_dashboard/export/csv/", views_admin.export_subscriptions_csv, name="export_subscriptions_csv"),
    path("sub_dashboard/add/", views_admin.subscription_add, name="subscription_add"),
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
