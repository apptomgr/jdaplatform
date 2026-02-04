from django.shortcuts import redirect, render, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from .paystack import initialize_payment
from .models import Payment
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription

import hmac
import hashlib
import logging
logger = logging.getLogger(__name__)


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
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
    except Exception as e:
        messages.error(request, f"Payment initialization error: {str(e)}")
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
            "status": "pending",
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
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
    except Exception as e:
        messages.error(request, f"Payment initialization error: {str(e)}")
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
            "status": "pending",
            "raw_response": result,
        }
    )

    authorization_url = result["data"].get("authorization_url")
    if not authorization_url:
        messages.error(request, "Could not retrieve Paystack authorization URL.")
        return redirect("jdasubscriptions:subscription_plan_list")

    return redirect(authorization_url)





#///////////////////////////////////////////paystack_webhook//////////////////////////////////////
@csrf_exempt
def paystack_webhook(request):
    """
    Paystack Webhook (SOURCE OF TRUTH)
    Handles charge.success events securely and idempotently
    """

    # --------------------------------------------------
    # 1️⃣ Verify Paystack signature
    # --------------------------------------------------
    paystack_signature = request.headers.get("x-paystack-signature")
    if not paystack_signature:
        return HttpResponse(status=400)

    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=request.body,
        digestmod=hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, paystack_signature):
        logger.warning("❌ Invalid Paystack signature")
        return HttpResponse(status=403)

    # --------------------------------------------------
    # 2️⃣ Parse payload
    # --------------------------------------------------
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    event = payload.get("event")
    data = payload.get("data") or {}

    logger.warning(f"📩 PAYSTACK WEBHOOK EVENT: {event}")

    # --------------------------------------------------
    # 3️⃣ Only handle successful charges
    # --------------------------------------------------
    if event != "charge.success":
        return HttpResponse(status=200)

    reference = data.get("reference")
    metadata = data.get("metadata") or {}

    if not reference:
        logger.error("❌ Missing payment reference")
        return HttpResponse(status=400)

    # --------------------------------------------------
    # 4️⃣ Verify transaction with Paystack (extra safety)
    # --------------------------------------------------
    verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(verify_url, headers=headers, timeout=15)
        verification = response.json()
    except Exception:
        logger.exception("❌ Paystack verification failed")
        return HttpResponse(status=500)

    if not verification.get("status"):
        logger.error("❌ Verification response invalid")
        return HttpResponse(status=400)

    verified_data = verification.get("data") or {}

    if verified_data.get("status") != "success":
        logger.warning("⚠️ Payment not successful")
        return HttpResponse(status=200)

    # --------------------------------------------------
    # 5️⃣ Idempotent Payment record
    # --------------------------------------------------
    payment, created = Payment.objects.get_or_create(
        reference=reference,
        defaults={
            "user_id": metadata.get("user_id"),
            "amount":verified_data.get("amount", 0) / 100,
            # Paystack sends amount in kobo-like units (XOF * 100)
            #"amount": verified_data.get("amount"),  # XOF → no division
            "status": "success",
            "raw_response": verified_data,
        },
    )

    if not created and payment.status == "success":
        logger.warning("🔁 Payment already processed")
        return HttpResponse(status=200)

    # --------------------------------------------------
    # 6️⃣ Activate subscription
    # --------------------------------------------------
    subscription_id = metadata.get("subscription_id")
    subscription_type = metadata.get("subscription_type")

    if not subscription_id or not subscription_type:
        logger.error("❌ Invalid subscription metadata")
        return HttpResponse(status=400)

    now = timezone.now()

    try:
        if subscription_type == "customer":
            subscription = CustomerSubscription.objects.get(
                id=subscription_id,
                status="draft",
            )

            CustomerSubscription.objects.filter(
                user=subscription.user,
                status="active",
            ).update(status="expired", ends_at=now)

        elif subscription_type == "institution":
            subscription = InstitutionSubscription.objects.get(
                id=subscription_id,
                status="draft",
            )

            InstitutionSubscription.objects.filter(
                user=subscription.user,
                status="active",
            ).update(status="expired", ends_at=now)

        else:
            logger.error("❌ Unknown subscription type")
            return HttpResponse(status=400)

    except (CustomerSubscription.DoesNotExist, InstitutionSubscription.DoesNotExist):
        logger.warning("⚠️ Subscription already processed or missing")
        return HttpResponse(status=200)

    # --------------------------------------------------
    # 7️⃣ Finalize subscription
    # --------------------------------------------------
    subscription.status = "active"
    subscription.starts_at = now
    subscription.paystack_reference = reference
    subscription.paystack_status = "success"
    subscription.save()

    payment.status = "success"
    payment.save()

    logger.warning("✅ Subscription activated via webhook")
    return HttpResponse(status=200)



#/////////////////////////////////////////payment_success/////////////////////////////////////
def payment_success(request):
    """
    Page shown to user after successful payment
    """
    return render(request, "jdapayments/payment_success.html")
