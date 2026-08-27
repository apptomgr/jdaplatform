from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from django.utils import timezone

from .paystack import initialize_payment
from .models import Payment
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription


@login_required
def initialize_customer_payment(request, subscription_id):
    """
    Initialize a Paystack payment for a CustomerSubscription (draft only).
    """

    try:
        subscription = CustomerSubscription.objects.get(
            id=subscription_id,
            user=request.user,
            status="draft"
        )
    except CustomerSubscription.DoesNotExist:
        messages.error(request, "No pending customer subscription found.")
        return redirect("jdasubscriptions:subscription_plan_list")

    # ✅ XOF has no subunit → DO NOT multiply by 100
    #amount = int(subscription.plan.price_fcfa)
    amount = int(subscription.plan.price_fcfa * 100)  # Due to Paystack internally normalizing XOF similar to user currencies although XOF has no subunits


    # Generate Paystack reference once per subscription
    if not subscription.paystack_reference:
        subscription.paystack_reference = (
            f"cusub_{subscription.id}_{int(timezone.now().timestamp())}"
        )
        subscription.save(update_fields=["paystack_reference"])

    metadata = {
        "subscription_id": subscription.id,
        "subscription_type": "customer",
        "user_id": subscription.user.id,
    }

    payload = {
        "email": subscription.user.email,
        "amount": amount,
        "currency": "XOF",
        "reference": subscription.paystack_reference,
        "metadata": metadata,
        "callback_url": request.build_absolute_uri(
            "/jdasubscriptions/paystack/callback/"
        ),
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
    except (Exception, requests.exceptions.Timeout) as e:
        messages.error(
            request,
            "Payment service timed out. Please try again or "
            "contact us at info@jda-ci.com"
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    if not result.get("status") or not result.get("data"):
        messages.error(
            request,
            result.get("message", "Failed to initialize payment with Paystack.")
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    Payment.objects.update_or_create(
        reference=subscription.paystack_reference,
        defaults={
            "user": subscription.user,
            "amount": subscription.plan.price_fcfa,
            "status": "initialized",
            "raw_response": result,
        }
    )

    authorization_url = result["data"].get("authorization_url")
    if not authorization_url:
        messages.error(request, "Could not retrieve Paystack authorization URL.")
        return redirect("jdasubscriptions:subscription_plan_list")

    return redirect(authorization_url)

#////////////////////////////////////////initialize_institution_payment//////////////////////////
@login_required
def initialize_institution_payment(request, subscription_id):
    """
    Initialize a Paystack payment for an InstitutionSubscription (draft only).
    Redirects user to Paystack payment page.
    """

    try:
        subscription = InstitutionSubscription.objects.get(
            id=subscription_id,
            user=request.user,
            status="draft"
        )
    except InstitutionSubscription.DoesNotExist:
        messages.error(request, "No pending institution subscription found.")
        return redirect("jdasubscriptions:subscription_plan_list")

    # ✅ XOF has no subunit → DO NOT multiply by 100
    #amount = int(subscription.plan.price_fcfa)
    amount = int(subscription.plan.price_fcfa * 100)


    # ✅ Generate Paystack reference ONCE per subscription
    if not subscription.paystack_reference:
        subscription.paystack_reference = (
            f"instsub_{subscription.id}_{int(timezone.now().timestamp())}"
        )
        subscription.save(update_fields=["paystack_reference"])

    metadata = {
        "subscription_id": subscription.id,
        "subscription_type": "institution",
        "user_id": subscription.user.id,
    }

    payload = {
        "email": subscription.user.email,
        "amount": amount,
        "currency": "XOF",
        "reference": subscription.paystack_reference,
        "metadata": metadata,
        "callback_url": request.build_absolute_uri(
            "/jdasubscriptions/paystack/callback/"
        ),
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    url = f"{settings.PAYSTACK_BASE_URL}/transaction/initialize"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()
    except (Exception, requests.exceptions.Timeout) as e:
        messages.error(
            request,
            "Payment service timed out. Please try again or "
            "contact us at info@jda-ci.com"
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    if not result.get("status") or not result.get("data"):
        messages.error(
            request,
            result.get("message", "Failed to initialize payment with Paystack.")
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    # ✅ Idempotent Payment persistence
    Payment.objects.update_or_create(
        reference=subscription.paystack_reference,
        defaults={
            "user": subscription.user,
            "amount": subscription.plan.price_fcfa,
            "status": "initialized",
            "raw_response": result,
        }
    )

    authorization_url = result["data"].get("authorization_url")
    if not authorization_url:
        messages.error(request, "Could not retrieve Paystack authorization URL.")
        return redirect("jdasubscriptions:subscription_plan_list")

    return redirect(authorization_url)

#/////////////////////////////////////////payment_success/////////////////////////////////////
def payment_success(request):
    """
    Page shown to user after successful payment
    """
    return render(request, "jdapayments/payment_success.html")
