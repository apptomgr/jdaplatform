from django.urls import path
from .views import (
    initialize_customer_payment,
    initialize_institution_payment,
    payment_success,
)

urlpatterns = [
    path("customer/<int:subscription_id>/initialize/", initialize_customer_payment, name="initialize_customer_payment"),
    path("institution/<int:subscription_id>/initialize/", initialize_institution_payment, name="initialize_institution_payment"),
    path("success/", payment_success, name="payment_success"),
]
