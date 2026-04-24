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
        try:
            subscription = CustomerSubscription.objects.get(
                id=subscription_id,
                user=request.user,
                status="draft",
            )
        except CustomerSubscription.DoesNotExist:
            messages.error(
                request,
                "Subscription not found or already activated. "
                "Please contact us at info@jda-ci.com"
            )
            return redirect("jdasubscriptions:subscription_failed")

        # Expire previous active subscriptions
        CustomerSubscription.objects.filter(
            user=request.user,
            status="active",
        ).update(status="expired", ends_at=now)

    elif subscription_type == "institution":
        try:
            subscription = InstitutionSubscription.objects.get(
                id=subscription_id,
                user=request.user,
                status="draft",
            )
        except InstitutionSubscription.DoesNotExist:
            messages.error(
                request,
                "Subscription not found or already activated. "
                "Please contact us at info@jda-ci.com"
            )
            return redirect("jdasubscriptions:subscription_failed")

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

# def subscription_plan_list(request):
#
#     plan_type = request.GET.get("type")  # 'individual' or 'institution'
#
#     plans = SubscriptionPlan.objects.filter(is_active=True)
#
#     # 🔥 mapping layer (important)
#     type_mapping = {
#         "individual": "customer",
#         "institution": "institution",
#     }
#
#     if plan_type in type_mapping:
#         plans = plans.filter(plan_type=type_mapping[plan_type])
#
#     context = {
#         "plans": plans,
#         "selected_type": plan_type,
#     }
#
#     return render(request, "jdasubscriptions/subscription_plan_list.html", context)




#//////////////////////////////////////select_subscription_plan/////////////////////////////////////////////////

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, CustomerSubscription, InstitutionSubscription
from jdapayments.views import (initialize_customer_payment,initialize_institution_payment,)
from jdasubscriptions.services.access_services import _get_active_subscription


@login_required
def select_subscription_plan(request, plan_id):
    """
    Create a DRAFT subscription for the selected plan,
    then redirect to Paystack initialization.
    """

    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    user = request.user

    if request.user.is_staff or request.user.is_superuser:
        messages.info(
            request,
            "Staff and admin accounts have full access — "
            "no subscription required."
        )
        return redirect('jdapublicationsapp_pubs')

    # -------------------------
    # Cross-model active subscription check
    # -------------------------
    if plan.plan_type == 'customer':
        has_institution = InstitutionSubscription.objects.filter(
            user=user, status='active'
        ).exists()
        if has_institution:
            messages.warning(
                request,
                "You already have an active institutional subscription. "
                "Please contact support to switch plans."
            )
            return redirect('jdapublicationsapp_pubs')

    elif plan.plan_type == 'institution':
        has_customer = CustomerSubscription.objects.filter(
            user=user, status='active'
        ).exists()
        if has_customer:
            messages.warning(
                request,
                "You already have an active customer subscription. "
                "Please contact support to switch plans."
            )
            return redirect('jdapublicationsapp_pubs')

    # -------------------------
    # Existing subscription check
    # -------------------------
    existing_subscription = _get_active_subscription(user)

    if existing_subscription:
        current_plan = existing_subscription.plan

        if current_plan.id == plan.id:
            messages.info(
                request,
                f"You are already subscribed to "
                f"{current_plan.name} ({current_plan.billing_period})."
            )
            return redirect('jdapublicationsapp_pubs')

        if not (request.method == 'POST' and request.POST.get('confirmed') == 'yes'):
            return render(request, 'jdasubscriptions/subscription_upgrade_confirm.html', {
                'current_plan': current_plan,
                'selected_plan': plan,
                'confirm_url': request.path,
            })

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

@login_required
def subscription_upgrade(request):
    return render(request, "jdasubscriptions/subscription_upgrade.html")


#//////////////////////////////////////public_subscription_plans/////////////////////////////////////////////////
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def public_subscription_plans(request):
    """
    Public endpoint — NO login required.
    Returns active subscription plans grouped by type and billing period.
    """
    type_param = request.GET.get('type', 'individual')
    billing_param = request.GET.get('billing', 'monthly')

    type_map = {'individual': 'customer', 'institution': 'institution'}
    plan_type = type_map.get(type_param, 'customer')

    billing_map = {'monthly': 'monthly', 'yearly': 'yearly', 'quarterly': 'quarterly'}
    billing_period = billing_map.get(billing_param, 'monthly')

    plans = SubscriptionPlan.objects.filter(
        plan_type=plan_type,
        billing_period=billing_period,
        is_active=True
    ).order_by('display_order', 'price_fcfa')

    # Build a lookup of yearly prices by plan name for cross-referencing
    yearly_lookup = {
        p.name: float(p.price_fcfa)
        for p in SubscriptionPlan.objects.filter(
            plan_type=plan_type, billing_period='yearly', is_active=True
        )
    }
    monthly_lookup = {
        p.name: float(p.price_fcfa)
        for p in SubscriptionPlan.objects.filter(
            plan_type=plan_type, billing_period='monthly', is_active=True
        )
    }

    # Mark most expensive plan as popular
    max_price = max((float(p.price_fcfa) for p in plans), default=0)

    result = []
    for plan in plans:
        features = plan.features if isinstance(plan.features, list) else []

        result.append({
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'price_monthly': monthly_lookup.get(plan.name),
            'price_yearly': yearly_lookup.get(plan.name),
            'currency': 'FCFA HT',
            'is_popular': float(plan.price_fcfa) == max_price,
            'subscribe_url': f'https://platform.jda-ci.com/jdasubscriptions/select/{plan.id}/',
            'features': features,
        })

    return JsonResponse({'plans': result})






