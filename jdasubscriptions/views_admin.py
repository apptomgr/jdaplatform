from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from .models import CustomerSubscription, InstitutionSubscription, SubscriptionPlan
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta, datetime, time
from jdasubscriptions.services.access_services import active_subscription_q
import json
import csv
from decimal import Decimal, ROUND_HALF_UP


@staff_member_required
def subscription_dashboard(request):
    now = timezone.now()

    customer_qs = CustomerSubscription.objects.select_related("user", "plan")
    institution_qs = InstitutionSubscription.objects.select_related("user", "plan")

    all_subscriptions = (
            normalize_subscriptions(customer_qs, "customer")
            + normalize_subscriptions(institution_qs, "institution")
    )

    #print(all_subscriptions[1])

    # KPIs
    total_subscriptions = len(all_subscriptions)
    active_subscriptions = [s for s in all_subscriptions if s["status"] == "active"]
    expired_subscriptions = [s for s in all_subscriptions if s["status"] == "expired"]

    #for i in active_subscriptions:
    #    print(i)

    # Breakdown helpers
    def count_by(field):
        result = {}
        for s in active_subscriptions:
            key = s[field]
            result[key] = result.get(key, 0) + 1
        return result

    ############
    now = timezone.now()

    #customer_subs = CustomerSubscription.objects.filter(status="active", starts_at__lte=now, ends_at__gte=now,).select_related("plan")
    #institution_subs = InstitutionSubscription.objects.filter(status="active", starts_at__lte=now, ends_at__gte=now, ).select_related("plan")

    customer_subs = CustomerSubscription.objects.filter(active_subscription_q())
    institution_subs = InstitutionSubscription.objects.filter(active_subscription_q())


    customer_mrr = subscription_mrr(customer_subs)
    institution_mrr = subscription_mrr(institution_subs)

    total_mrr = customer_mrr + institution_mrr
    total_arr = total_mrr * Decimal("12")

    ##############


    context = {
        "total_subscriptions": total_subscriptions,
        "active_count": len(active_subscriptions),
        "expired_count": len(expired_subscriptions),
        "by_subscriber_type": count_by("subscriber_type"),
        "by_plan_type": count_by("plan_type"),
        "by_billing_period": count_by("billing_period"),
        "expiring_soon": [
            s for s in active_subscriptions
            if s["ends_at"] and s["ends_at"] <= now + timezone.timedelta(days=30)
        ],
        "recent_activations": sorted(
            active_subscriptions,
            key=lambda x: x["starts_at"],
            reverse=True
        )[:10],
    }
    #mmr & ARR info
    context.update({
        "customer_mrr": customer_mrr,
        "institution_mrr": institution_mrr,
        "total_mrr": total_mrr,
        "total_arr": total_arr,
    })

    #chart info
    context.update({
        # Chart: Active vs Expired
        "active_vs_expired": {
            "active": len(active_subscriptions),
            "expired": len(expired_subscriptions),
        },

        # Chart: MRR breakdown
        "mrr_chart": {
            "customer": float(customer_mrr),
            "institution": float(institution_mrr),
        },
    })

    context.update({
        "mrr_chart_json": json.dumps([
            quantize_2(customer_mrr),
            quantize_2(institution_mrr),
        ]),
    })

    return render(request, "jdasubscriptions/admin/dashboard.html", context)



#//////////////////////////////////////
def quantize_2(value):
    return float(
        Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )
#////////////////////////////////////////////////normalize_subscriptions////////////////////////////////////////////
def normalize_subscriptions(qs, subscriber_type):
    """
    Convert CustomerSubscription or InstitutionSubscription
    into a unified structure for dashboard rendering
    """
    return [
        {
            "subscriber_type": subscriber_type,
            "user": sub.user,
            "plan": sub.plan,
            "status": sub.status,
            "billing_period": sub.plan.billing_period,
            "plan_type": sub.plan.plan_type,
            "starts_at": sub.starts_at,
            "ends_at": sub.ends_at,
        }
        for sub in qs
    ]

#//////////////////////////////////////////////subscription_mrr///////////////////////////////////////////////////
from decimal import Decimal

def subscription_mrr(subscriptions):
    mrr = Decimal("0.00")

    for sub in subscriptions:
        price = sub.plan.price_fcfa

        if sub.plan.billing_period == "monthly":
            mrr += price
        elif sub.plan.billing_period == "quarterly":
            mrr += price / Decimal("3")
        elif sub.plan.billing_period == "yearly":
            mrr += price / Decimal("12")

    return mrr


# ========== Sub Dashboard ==========

def _staff_only(request):
    """
    Returns a redirect response if the user is not staff/superuser,
    otherwise returns None (access granted).
    """
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.warning(request, "You don't have access to the Subscription Dashboard.")
        return redirect('jdapublicationsapp_pubs')
    return None


def _apply_sub_filters(customer_qs, institution_qs, params):
    """Apply shared filter params to both subscriber querysets."""
    subscriber_type = params.get('subscriber_type', '')
    plan_id = params.get('plan', '')
    status_filter = params.get('status', '')
    date_from = params.get('date_from', '')
    date_to = params.get('date_to', '')

    if subscriber_type == 'customer':
        institution_qs = institution_qs.none()
    elif subscriber_type == 'institution':
        customer_qs = customer_qs.none()

    if plan_id:
        customer_qs = customer_qs.filter(plan_id=plan_id)
        institution_qs = institution_qs.filter(plan_id=plan_id)
    if status_filter:
        customer_qs = customer_qs.filter(status=status_filter)
        institution_qs = institution_qs.filter(status=status_filter)
    if date_from:
        customer_qs = customer_qs.filter(starts_at__date__gte=date_from)
        institution_qs = institution_qs.filter(starts_at__date__gte=date_from)
    if date_to:
        customer_qs = customer_qs.filter(starts_at__date__lte=date_to)
        institution_qs = institution_qs.filter(starts_at__date__lte=date_to)

    return customer_qs, institution_qs


def sub_dashboard(request):
    deny = _staff_only(request)
    if deny:
        return deny
    # Base querysets
    customer_qs = CustomerSubscription.objects.select_related('user', 'plan').order_by('-starts_at')
    institution_qs = InstitutionSubscription.objects.select_related('user', 'plan').order_by('-starts_at')

    # Apply filters
    customer_qs, institution_qs = _apply_sub_filters(customer_qs, institution_qs, request.GET)

    keyword = request.GET.get('keyword', '').strip()
    if keyword:
        kq = (
            Q(user__username__icontains=keyword) |
            Q(user__first_name__icontains=keyword) |
            Q(user__last_name__icontains=keyword) |
            Q(user__email__icontains=keyword)
        )
        customer_qs = customer_qs.filter(kq)
        institution_qs = institution_qs.filter(kq)

    # Summary stats (always unfiltered, across both models)
    total_active = (
        CustomerSubscription.objects.filter(status='active').count() +
        InstitutionSubscription.objects.filter(status='active').count()
    )
    total_expired = (
        CustomerSubscription.objects.filter(status='expired').count() +
        InstitutionSubscription.objects.filter(status='expired').count()
    )
    total_cancelled = 0  # No cancelled status in current model

    # Active breakdown by plan name (across both)
    customer_by_plan = (
        CustomerSubscription.objects.filter(status='active')
        .values('plan__name')
        .annotate(count=Count('id'))
    )
    institution_by_plan = (
        InstitutionSubscription.objects.filter(status='active')
        .values('plan__name')
        .annotate(count=Count('id'))
    )
    plan_breakdown = {}
    for row in customer_by_plan:
        plan_breakdown[row['plan__name']] = plan_breakdown.get(row['plan__name'], 0) + row['count']
    for row in institution_by_plan:
        plan_breakdown[row['plan__name']] = plan_breakdown.get(row['plan__name'], 0) + row['count']

    # Paginate each table separately
    customer_paginator = Paginator(customer_qs, 25)
    customer_page_obj = customer_paginator.get_page(request.GET.get('customer_page', 1))

    institution_paginator = Paginator(institution_qs, 25)
    institution_page_obj = institution_paginator.get_page(request.GET.get('institution_page', 1))

    # Plans for filter dropdown
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('name')

    # Filter query string (without page params) for pagination links
    filter_params = request.GET.copy()
    filter_params.pop('customer_page', None)
    filter_params.pop('institution_page', None)
    filter_query_string = filter_params.urlencode()

    from django.contrib.auth import get_user_model
    User = get_user_model()

    context = {
        'total_active': total_active,
        'total_expired': total_expired,
        'total_cancelled': total_cancelled,
        'plan_breakdown': plan_breakdown,
        'customer_page_obj': customer_page_obj,
        'institution_page_obj': institution_page_obj,
        'plans': plans,
        'filter_subscriber_type': request.GET.get('subscriber_type', ''),
        'filter_plan': request.GET.get('plan', ''),
        'filter_status': request.GET.get('status', ''),
        'filter_date_from': request.GET.get('date_from', ''),
        'filter_date_to': request.GET.get('date_to', ''),
        'filter_keyword': keyword,
        'filter_query_string': filter_query_string,
        'all_users': User.objects.all().order_by('username'),
        'all_plans': SubscriptionPlan.objects.filter(is_active=True).order_by('name'),
        'today': timezone.now().date(),
    }
    return render(request, 'jdasubscriptions/sub_dashboard.html', context)


@require_POST
def expire_subscription(request):
    deny = _staff_only(request)
    if deny:
        return deny
    pk = request.POST.get('subscription_pk')
    model_type = request.POST.get('model_type')
    if model_type == 'customer':
        sub = get_object_or_404(CustomerSubscription, pk=pk)
    elif model_type == 'institution':
        sub = get_object_or_404(InstitutionSubscription, pk=pk)
    else:
        messages.error(request, 'Invalid subscription type.')
        return redirect('jdasubscriptions:sub_dashboard')
    sub.status = 'expired'
    sub.ends_at = timezone.now()
    sub.save()
    messages.success(request, f'Subscription #{pk} has been marked as expired.')
    return redirect('jdasubscriptions:sub_dashboard')


@require_POST
def extend_subscription(request):
    deny = _staff_only(request)
    if deny:
        return deny
    pk = request.POST.get('subscription_pk')
    model_type = request.POST.get('model_type')
    try:
        extend_days = int(request.POST.get('extend_days', 30))
        extend_days = max(1, min(extend_days, 365))
    except (TypeError, ValueError):
        extend_days = 30
    if model_type == 'customer':
        sub = get_object_or_404(CustomerSubscription, pk=pk)
    elif model_type == 'institution':
        sub = get_object_or_404(InstitutionSubscription, pk=pk)
    else:
        messages.error(request, 'Invalid subscription type.')
        return redirect('jdasubscriptions:sub_dashboard')
    now = timezone.now()
    if sub.ends_at and sub.ends_at > now:
        sub.ends_at = sub.ends_at + timedelta(days=extend_days)
    else:
        sub.ends_at = now + timedelta(days=extend_days)
    if sub.status == 'expired':
        sub.status = 'active'
        if not sub.starts_at:
            sub.starts_at = now
    sub.save()
    messages.success(request, f'Subscription #{pk} extended by {extend_days} day(s). New end date: {sub.ends_at.strftime("%Y-%m-%d")}')
    return redirect('jdasubscriptions:sub_dashboard')


def export_subscriptions_csv(request):
    deny = _staff_only(request)
    if deny:
        return deny
    customer_qs = CustomerSubscription.objects.select_related('user', 'plan').order_by('-starts_at')
    institution_qs = InstitutionSubscription.objects.select_related('user', 'plan').order_by('-starts_at')
    customer_qs, institution_qs = _apply_sub_filters(customer_qs, institution_qs, request.GET)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'
    writer = csv.writer(response)
    writer.writerow(['#', 'Type', 'Name', 'Username', 'Email', 'Plan', 'Billing', 'Status', 'Start', 'End', 'Payment Ref'])

    row_num = 1
    for sub in customer_qs:
        name = f"{sub.user.first_name} {sub.user.last_name}".strip() or sub.user.username
        writer.writerow([
            row_num, 'Customer', name, sub.user.username, sub.user.email,
            sub.plan.name, sub.plan.billing_period, sub.status,
            sub.starts_at.strftime('%Y-%m-%d') if sub.starts_at else '',
            sub.ends_at.strftime('%Y-%m-%d') if sub.ends_at else '',
            sub.paystack_reference or '',
        ])
        row_num += 1
    for sub in institution_qs:
        name = f"{sub.user.first_name} {sub.user.last_name}".strip() or sub.user.username
        writer.writerow([
            row_num, 'Institution', name, sub.user.username, sub.user.email,
            sub.plan.name, sub.plan.billing_period, sub.status,
            sub.starts_at.strftime('%Y-%m-%d') if sub.starts_at else '',
            sub.ends_at.strftime('%Y-%m-%d') if sub.ends_at else '',
            sub.paystack_reference or '',
        ])
        row_num += 1
    return response


@require_POST
def subscription_add(request):
    deny = _staff_only(request)
    if deny:
        return deny
    if not request.user.is_superuser:
        messages.warning(request, "Only administrators can add subscriptions.")
        return redirect('jdasubscriptions:sub_dashboard')

    from django.contrib.auth import get_user_model
    from django.utils.dateparse import parse_date
    User = get_user_model()

    subscription_type = request.POST.get('subscription_type', 'customer')
    user_id = request.POST.get('user')
    plan_id = request.POST.get('plan')
    start_date_str = request.POST.get('start_date', '')
    end_date_str = request.POST.get('end_date', '')
    payment_reference = request.POST.get('payment_reference', '').strip() or None
    status = request.POST.get('status', 'active')

    try:
        user = User.objects.get(pk=user_id)
        plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
    except (User.DoesNotExist, SubscriptionPlan.DoesNotExist):
        messages.error(request, "Invalid user or plan selected.")
        return redirect('jdasubscriptions:sub_dashboard')

    starts_at = None
    ends_at = None
    d = parse_date(start_date_str)
    if d:
        starts_at = timezone.make_aware(datetime.combine(d, time.min))
    d = parse_date(end_date_str)
    if d:
        ends_at = timezone.make_aware(datetime.combine(d, time(23, 59, 59)))

    if status == 'active':
        existing_customer = CustomerSubscription.objects.filter(user=user, status='active').exists()
        existing_institution = InstitutionSubscription.objects.filter(user=user, status='active').exists()
        if existing_customer or existing_institution:
            messages.warning(
                request,
                f"{user.username} already has an active subscription. "
                f"Please expire or delete it before creating a new one."
            )
            return redirect('jdasubscriptions:sub_dashboard')

    try:
        if subscription_type == 'institution':
            InstitutionSubscription.objects.create(
                user=user,
                plan=plan,
                status=status,
                starts_at=starts_at,
                ends_at=ends_at,
                paystack_reference=payment_reference,
            )
        else:
            CustomerSubscription.objects.create(
                user=user,
                plan=plan,
                status=status,
                starts_at=starts_at,
                ends_at=ends_at,
                paystack_reference=payment_reference,
            )
    except Exception as e:
        messages.error(request, f"Could not create subscription: {e}")
        return redirect('jdasubscriptions:sub_dashboard')

    messages.success(request, f"Subscription created for {user.username} ({plan.name}).")
    return redirect('jdasubscriptions:sub_dashboard')


@require_POST
def delete_subscription(request, model_type, pk):
    if not request.user.is_superuser:
        messages.warning(request, "Only administrators can delete subscriptions.")
        return redirect('jdasubscriptions:sub_dashboard')

    if model_type == 'customer':
        obj = get_object_or_404(CustomerSubscription, pk=pk)
    elif model_type == 'institution':
        obj = get_object_or_404(InstitutionSubscription, pk=pk)
    else:
        messages.error(request, "Invalid subscription type.")
        return redirect('jdasubscriptions:sub_dashboard')

    username = obj.user.username
    plan_name = obj.plan.name
    obj.delete()
    messages.success(request, f"Subscription deleted: {username} — {plan_name}")
    return redirect('jdasubscriptions:sub_dashboard')
