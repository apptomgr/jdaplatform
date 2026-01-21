from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import SubscriptionPlan, CustomerSubscription, InstitutionSubscription
from django.utils import timezone
from dateutil.relativedelta import relativedelta


#//////////////////////////////////////subscription_plan_list/////////////////////////////////////////////////
@login_required
def subscription_plan_list(request):
    plan_type = request.GET.get("plan_type", "customer")
    billing_period = request.GET.get("billing_period", "monthly")

    plans = (SubscriptionPlan.objects.filter(plan_type=plan_type, billing_period=billing_period, is_active=True,).order_by("display_order"))

    context = {"plans": plans, "plan_type": plan_type, "billing_period": billing_period,}
    return render(request, "jdasubscriptions/subscription_plan_list.html", context,)


#//////////////////////////////////////select_subscription_plan/////////////////////////////////////////////////
#from django.contrib.auth.decorators import login_required
#from django.shortcuts import get_object_or_404, redirect
#from django.http import HttpResponseBadRequest

@login_required
def select_subscription_plan(request, plan_id):
    """
    Create a DRAFT subscription for the selected plan.
    Handles both customer and institution plans.
    """

    plan = get_object_or_404(
        SubscriptionPlan,
        id=plan_id,
        is_active=True,
    )

    user = request.user

    # -------------------------
    # CUSTOMER PLAN
    # -------------------------
    if plan.plan_type == "customer":

        # Remove any existing draft
        CustomerSubscription.objects.filter(
            user=user,
            status="draft"
        ).delete()

        CustomerSubscription.objects.create(
            user=user,
            plan=plan,
            status="draft"
        )

        return redirect("jdasubscriptions:subscription_confirm")

    # -------------------------
    # INSTITUTION PLAN
    # -------------------------
    elif plan.plan_type == "institution":

        InstitutionSubscription.objects.filter(
            user=user,
            status="draft"
        ).delete()

        InstitutionSubscription.objects.create(
            user=user,
            plan=plan,
            status="draft"
        )

        return redirect("jdasubscriptions:institution_subscription_confirm")

    # -------------------------
    # SAFETY NET
    # -------------------------
    return HttpResponseBadRequest("Invalid subscription plan type")

# @login_required
# def select_subscription_plan(request, plan_id):
#     print(f"25 - selecting a plan - plan id: {plan_id}")
#     plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True, plan_type="customer")
#     print(f"26 Plan ID: {plan_id} - plan: {plan}")
#
#     # Remove any existing draft
#     CustomerSubscription.objects.filter(user=request.user, status="draft").delete()
#
#     # Create new draft subscription
#     CustomerSubscription.objects.create(user=request.user, plan=plan, status="draft")
#
#     return redirect("jdasubscriptions:subscription_confirm")



#///////////////////////////////////////subscription_confirm////////////////////////////////////////////
@login_required
def subscription_confirm(request):
    # Get draft subscription
    subscription = get_object_or_404(
        CustomerSubscription,
        user=request.user,
        status="draft"
    )

    now = timezone.now()

    # Expire any existing active subscription
    CustomerSubscription.objects.filter(
        user=request.user,
        status="active"
    ).update(status="expired", ends_at=now)

    # Calculate end date
    if subscription.plan.billing_period == "monthly":
        ends_at = now + relativedelta(months=1)
    elif subscription.plan.billing_period == "quarterly":
        ends_at = now + relativedelta(months=3)
    elif subscription.plan.billing_period == "yearly":
        ends_at = now + relativedelta(years=1)
    else:
        return HttpResponseBadRequest("Invalid billing period")

    # Activate subscription
    subscription.status = "active"
    subscription.starts_at = now
    subscription.ends_at = ends_at
    subscription.save()

    messages.success(
        request,
        "Your subscription is now active. Welcome aboard!"
    )

    # Redirect user back to publications
    return redirect("jdapublicationsapp_pubs")


#/////////////////////////////////////////////institution_subscription_confirm////////////////////////////
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .models import InstitutionSubscription


@login_required
def institution_subscription_confirm(request):
    """
    Activate an institution subscription (single-user institution).
    """

    # Get draft subscription
    subscription = get_object_or_404(
        InstitutionSubscription,
        user=request.user,
        status="draft"
    )

    now = timezone.now()

    # Expire any existing active subscription
    InstitutionSubscription.objects.filter(
        user=request.user,
        status="active"
    ).update(
        status="expired",
        ends_at=now
    )

    # Calculate end date
    billing_period = subscription.plan.billing_period

    if billing_period == "monthly":
        ends_at = now + relativedelta(months=1)
    elif billing_period == "quarterly":
        ends_at = now + relativedelta(months=3)
    elif billing_period == "yearly":
        ends_at = now + relativedelta(years=1)
    else:
        return HttpResponseBadRequest("Invalid billing period")

    # Activate subscription
    subscription.status = "active"
    subscription.starts_at = now
    subscription.ends_at = ends_at
    subscription.save()

    messages.success(
        request,
        "Your institutional subscription is now active."
    )

    # Redirect to publications
    return redirect("jdapublicationsapp_pubs")


#///////////////////////////////////////subscription_success////////////////////////////////////////////////////
@login_required
def subscription_success(request):
    return render(request,"jdasubscriptions/subscription_success.html")




