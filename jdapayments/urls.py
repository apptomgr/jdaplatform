from django.urls import path
from .views import (
    initialize_customer_payment,
    initialize_institution_payment,
    paystack_webhook,
    payment_success,
)

urlpatterns = [
    path("customer/<int:subscription_id>/initialize/", initialize_customer_payment, name="initialize_customer_payment"),
    path("institution/<int:subscription_id>/initialize/", initialize_institution_payment, name="initialize_institution_payment"),
    #path("paystack/webhook/", paystack_webhook, name="paystack_webhook"),
    path("paystack/webhook/", paystack_webhook.paystack_webhook, name="paystack_webhook"),
    path("success/", payment_success, name="payment_success"),
]



#urlpatterns = [
#    path("paystack/webhook/", webhooks.paystack_webhook, name="paystack_webhook"),
#]
