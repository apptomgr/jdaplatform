import hashlib
import hmac
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import SubscriptionPlan, CustomerSubscription, InstitutionSubscription
from django.utils import timezone
from jdapayments.paystack import initialize_payment, verify_payment

from django.conf import settings
import logging
logger = logging.getLogger(__name__)

from .payment_activation import (
    activate_subscription_from_verified_payment,
    STATUS_ACTIVATED,
    STATUS_ALREADY_PROCESSED,
    STATUS_INVALID_METADATA,
    STATUS_SUBSCRIPTION_NOT_FOUND,
    STATUS_UNKNOWN_SUBSCRIPTION_TYPE,
)


@login_required
def paystack_callback(request):
    """
    Browser-redirect fast-path: verifies the payment and activates the
    subscription immediately so the customer sees "active" without waiting
    on webhook delivery. Delegates the actual activation to
    activate_subscription_from_verified_payment, shared with
    paystack_webhook below — if this redirect never happens (closed tab,
    dropped connection), the webhook still completes activation on its own.
    """

    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "Missing payment reference.")
        return redirect("jdasubscriptions:subscription_plan_list")

    logger.warning(f"🔥 PAYSTACK CALLBACK HIT: {reference}")

    try:
        result = verify_payment(reference)
    except Exception:
        logger.exception("Paystack verification error")
        messages.error(request, "Unable to verify payment.")
        return redirect("jdasubscriptions:subscription_plan_list")

    if not result.get("status"):
        messages.error(
            request,
            result.get("message", "Payment verification failed.")
        )
        return redirect("jdasubscriptions:subscription_plan_list")

    verified_data = result.get("data") or {}
    logger.warning(f"PAYSTACK DATA: {verified_data}")

    if verified_data.get("status") != "success":
        messages.error(request, "Payment was not successful.")
        return redirect("jdasubscriptions:subscription_plan_list")

    activation = activate_subscription_from_verified_payment(reference, verified_data)

    if activation.status == STATUS_ALREADY_PROCESSED:
        return redirect("jdasubscriptions:subscription_success")

    if activation.status == STATUS_ACTIVATED:
        messages.success(request, "Your subscription is now active 🎉")
        return redirect("jdasubscriptions:subscription_success")

    if activation.status == STATUS_INVALID_METADATA:
        messages.error(request, "Invalid payment metadata.")
        return redirect("jdasubscriptions:subscription_plan_list")

    if activation.status == STATUS_UNKNOWN_SUBSCRIPTION_TYPE:
        messages.error(request, "Unknown subscription type.")
        return redirect("jdasubscriptions:subscription_plan_list")

    # STATUS_SUBSCRIPTION_NOT_FOUND
    messages.error(
        request,
        "Subscription not found or already activated. "
        "Please contact us at info@jda-ci.com"
    )
    return redirect("jdasubscriptions:subscription_failed")


# Documented Paystack webhook-sending IPs (identical for test and live
# mode). Logged against on mismatch only, never hard-enforced — DigitalOcean
# App Platform likely proxies requests, so REMOTE_ADDR may not reflect
# Paystack's real source IP unless a forwarded-for header is correctly
# trusted, which hasn't been confirmed for this environment. Signature
# verification below is the real authenticity check; a wrong IP-detection
# implementation would silently reject every genuine webhook call, which is
# a worse failure mode than skipping a secondary check.
PAYSTACK_WEBHOOK_IPS = {"52.31.139.75", "52.49.173.169", "52.214.14.220"}


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """
    Server-to-server Paystack webhook: the reliable primary activation
    path, independent of the customer's browser completing a redirect.
    Verifies the HMAC-SHA512 signature, re-verifies the transaction via
    Paystack's Verify API (never trusts the webhook payload alone), then
    delegates to the same activate_subscription_from_verified_payment used
    by paystack_callback.
    """
    raw_body = request.body

    signature = request.headers.get("x-paystack-signature", "")
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        raw_body,
        hashlib.sha512,
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, signature):
        logger.warning("Paystack webhook: signature mismatch, rejecting.")
        return HttpResponse(status=403)

    source_ip = request.META.get("REMOTE_ADDR")
    if source_ip not in PAYSTACK_WEBHOOK_IPS:
        logger.warning(
            f"Paystack webhook: request from unrecognized IP {source_ip} "
            "(signature valid — not rejecting, logged for visibility only)."
        )

    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("Paystack webhook: malformed JSON body.")
        return HttpResponse(status=400)

    event = payload.get("event")
    if event != "charge.success":
        logger.info(f"Paystack webhook: ignoring event type {event!r}.")
        return HttpResponse(status=200)

    reference = (payload.get("data") or {}).get("reference")
    if not reference:
        logger.warning("Paystack webhook: charge.success event missing reference.")
        return HttpResponse(status=200)

    try:
        result = verify_payment(reference)
    except Exception:
        logger.exception(f"Paystack webhook: verify_payment call failed for {reference}.")
        return HttpResponse(status=500)

    if not result.get("status"):
        logger.warning(
            f"Paystack webhook: verify_payment returned failure for {reference}: "
            f"{result.get('message')}"
        )
        return HttpResponse(status=502)

    verified_data = result.get("data") or {}
    if verified_data.get("status") != "success":
        logger.info(
            f"Paystack webhook: transaction {reference} not successful per "
            f"Verify API ({verified_data.get('status')})."
        )
        return HttpResponse(status=200)

    try:
        activation = activate_subscription_from_verified_payment(reference, verified_data)
    except Exception:
        logger.exception(f"Paystack webhook: unexpected error activating subscription for {reference}.")
        return HttpResponse(status=500)

    if activation.status in (STATUS_ACTIVATED, STATUS_ALREADY_PROCESSED):
        return HttpResponse(status=200)

    # Data problem (invalid metadata / subscription not found / unknown
    # type) — retrying won't fix bad data, so acknowledge to stop Paystack's
    # retries. Logged loudly; the Payment row stays "initialized" (never
    # flipped to "success"), which is exactly what makes it recoverable via
    # the admin "Reprocess selected payments" action.
    logger.error(
        f"Paystack webhook: activation did not complete for {reference}: "
        f"{activation.status} — {activation.message}"
    )
    return HttpResponse(status=200)


#//////////////////////////////////////subscription_plan_list/////////////////////////////////////////////////
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
    quarterly_lookup = {
        p.name: float(p.price_fcfa)
        for p in SubscriptionPlan.objects.filter(
            plan_type=plan_type, billing_period='quarterly', is_active=True
        )
    }

    result = []
    for plan in plans:
        features = plan.features if isinstance(plan.features, list) else []

        result.append({
            'id': plan.id,
            'name': plan.name,
            'description': plan.description,
            'price_monthly': monthly_lookup.get(plan.name),
            'price_quarterly': quarterly_lookup.get(plan.name),
            'price_yearly': yearly_lookup.get(plan.name),
            'currency': 'FCFA TTC',
            'is_popular': plan.name == 'Akwaba Gold',
            'subscribe_url': request.build_absolute_uri(f'/jdasubscriptions/select/{plan.id}/'),
            'features': features,
        })

    return JsonResponse({'plans': result})






