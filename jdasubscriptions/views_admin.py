from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .models import CustomerSubscription, InstitutionSubscription
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from jdasubscriptions.services.access_services import active_subscription_q
import json
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
