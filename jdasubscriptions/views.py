from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import SubscriptionPlan, CustomerSubscription, InstitutionSubscription
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from jdapayments.paystack import initialize_payment, verify_payment
from django.contrib import messages

from jdapayments.models import Payment
from jdapayments.paystack import verify_payment
import requests

from django.conf import settings
import logging
logger = logging.getLogger(__name__)

#import requests
#import logging
#from django.conf import settings
#from django.contrib import messages
from django.shortcuts import redirect
#from django.utils import timezone
#from django.contrib.auth.decorators import login_required

#from jdasubscriptions.models import (
#    CustomerSubscription,
#    InstitutionSubscription,
#)
#from jdapayments.models import Payment

#logger = logging.getLogger(__name__)


@login_required
def paystack_callback(request):
    """
    Paystack payment verification + subscription activation
    """

    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "Missing payment reference.")
        return redirect("jdasubscriptions:subscription_plan_list")

    logger.warning(f"🔥 PAYSTACK CALLBACK HIT: {reference}")

    # --------------------------------------------------
    # 1️⃣ Verify payment with Paystack
    # --------------------------------------------------
    verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(verify_url, headers=headers, timeout=15)
        result = response.json()
    except Exception as e:
        logger.exception("Paystack verification error")
        messages.error(request, "Unable to verify payment.")
        return redirect("jdasubscriptions:subscription_plan_list")

    if not result.get("status"):
        messages.error(
            request,
            result.get("message", "Payment verification failed.")
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    data = result.get("data") or {}
    metadata = data.get("metadata") or {}

    logger.warning(f"PAYSTACK DATA: {data}")
    logger.warning(f"PAYSTACK METADATA: {metadata}")

    # --------------------------------------------------
    # 2️⃣ Ensure payment success
    # --------------------------------------------------
    if data.get("status") != "success":
        messages.error(request, "Payment was not successful.")
        return redirect("jdasubscriptions:subscription_plan_list")

    # --------------------------------------------------
    # 3️⃣ Idempotency (Payment-level)
    # --------------------------------------------------
    payment, created = Payment.objects.get_or_create(
        reference=reference,
        defaults={
            "user": request.user,
            "amount": data.get("amount", 0),
            "status": "success",
            "raw_response": data,
        },
    )

    if not created and payment.status == "success":
        logger.warning("Payment already processed.")
        return redirect("jdasubscriptions:subscription_success")

    # --------------------------------------------------
    # 4️⃣ Extract subscription metadata
    # --------------------------------------------------
    subscription_id = metadata.get("subscription_id")
    subscription_type = metadata.get("subscription_type")

    if not subscription_id or not subscription_type:
        messages.error(request, "Invalid payment metadata.")
        return redirect("jdasubscriptions:subscription_plan_list")

    now = timezone.now()

    # --------------------------------------------------
    # 5️⃣ Activate the correct subscription
    # --------------------------------------------------
    if subscription_type == "customer":
        subscription = CustomerSubscription.objects.get(
            id=subscription_id,
            user=request.user,
            status="draft",
        )

        # Expire previous active subscriptions
        CustomerSubscription.objects.filter(
            user=request.user,
            status="active",
        ).update(status="expired", ends_at=now)

    elif subscription_type == "institution":
        subscription = InstitutionSubscription.objects.get(
            id=subscription_id,
            user=request.user,
            status="draft",
        )

        InstitutionSubscription.objects.filter(
            user=request.user,
            status="active",
        ).update(status="expired", ends_at=now)

    else:
        messages.error(request, "Unknown subscription type.")
        return redirect("jdasubscriptions:subscription_plan_list")

    # --------------------------------------------------
    # 6️⃣ Activate subscription
    # --------------------------------------------------
    subscription.status = "active"
    subscription.starts_at = now
    subscription.paystack_reference = reference
    subscription.paystack_status = "success"
    subscription.save()

    # --------------------------------------------------
    # 7️⃣ Finalize payment record
    # --------------------------------------------------
    payment.status = "success"
    payment.save()

    messages.success(request, "Your subscription is now active 🎉")
    return redirect("jdasubscriptions:subscription_success")


#//////////////////////////////////////subscription_plan_list/////////////////////////////////////////////////
@login_required
def subscription_plan_list(request):
    plan_type = request.GET.get("plan_type", "customer")
    billing_period = request.GET.get("billing_period", "monthly")

    plans = SubscriptionPlan.objects.filter(
        plan_type=plan_type,
        billing_period=billing_period,
        is_active=True
    ).order_by("display_order")

    context = {
        "plans": plans,
        "plan_type": plan_type,
        "billing_period": billing_period,
    }
    return render(request, "jdasubscriptions/subscription_plan_list.html", context)



#//////////////////////////////////////select_subscription_plan/////////////////////////////////////////////////

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, CustomerSubscription, InstitutionSubscription
from jdapayments.views import (initialize_customer_payment,initialize_institution_payment,)


@login_required
def select_subscription_plan(request, plan_id):
    """
    Create a DRAFT subscription for the selected plan,
    then redirect to Paystack initialization.
    """

    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    user = request.user

    #print(f"129 user: {user} - plan: {plan}")

    # -------------------------
    # CUSTOMER PLAN
    # -------------------------
    if plan.plan_type == "customer":
        # Remove any existing draft
        CustomerSubscription.objects.filter(user=user, status="draft").delete()

        draft = CustomerSubscription.objects.create(
            user=user,
            plan=plan,
            status="draft"
        )
        #print(f"143; draft: {draft}")
        # Redirect to payment initialization
        return initialize_customer_payment(request, draft.id)

    # -------------------------
    # INSTITUTION PLAN
    # -------------------------
    elif plan.plan_type == "institution":
        InstitutionSubscription.objects.filter(user=user, status="draft").delete()

        draft = InstitutionSubscription.objects.create(
            user=user,
            plan=plan,
            status="draft"
        )

        return initialize_institution_payment(request, draft.id)

    # -------------------------
    # SAFETY NET
    # -------------------------
    return HttpResponseBadRequest("Invalid subscription plan type")



#///////////////////////////////////////subscription_success////////////////////////////////////////////////////
@login_required
def subscription_success(request):
    return render(request,"jdasubscriptions/subscription_success.html")


#///////////////////////////////////////subscription_failed////////////////////////////////////////////////////
@login_required
def subscription_failed(request):
    return render(request, "jdasubscriptions/subscription_failed.html")



#///////////////////////////////////////subscription_upgrade////////////////////////////////////////////////////

def subscription_upgrade(request):
    return render(request, "jdasubscriptions/subscription_upgrade.html")






