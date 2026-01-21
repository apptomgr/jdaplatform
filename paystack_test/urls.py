from django.urls import path
from . import views

app_name = "paystack_test"

urlpatterns = [
    path("", views.payment_page, name="payment_page"),
    path("start/", views.start_payment, name="start_payment"),
    path("callback/", views.payment_callback, name="payment_callback"),
    path("webhook/", views.paystack_webhook, name="paystack_webhook"),
]
