from django.conf import settings
from django.utils import timezone
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription, SubscriptionPlan
from django.db.models import Q

#/////////////////////////////////////////////_get_active_subscription///////////////////////////////
def _get_active_subscription(user):
    """
    Returns active subscription (Institution first, then Customer)
    """

    if not user or not user.is_authenticated:
        return None

    now = timezone.now()

    # 1️⃣ Institution subscription FIRST (priority)
    institution_sub = (
        InstitutionSubscription.objects
            .select_related("plan")
            .filter(
            user=user,
            status="active",
            starts_at__lte=now
        )
            .filter(
            Q(ends_at__isnull=True) | Q(ends_at__gte=now)
        )
            .order_by("-created_at")
            .first()
    )

    if institution_sub:
        return institution_sub

    # 2️⃣ Customer subscription SECOND
    customer_sub = (
        CustomerSubscription.objects
            .select_related("plan")
            .filter(
            user=user,
            status="active",
            starts_at__lte=now
        )
            .filter(
            Q(ends_at__isnull=True) | Q(ends_at__gte=now)
        )
            .order_by("-created_at")
            .first()
    )

    if customer_sub:
        return customer_sub

    return None


#///////////////////////////////////////////user_has_active_subscription/////////////////////////////
def user_has_active_subscription(user):
    if not getattr(settings, 'SUBSCRIPTION_REQUIRED', True):
        return True
    return _get_active_subscription(user) is not None





#///////////////////////////////////user_can_access_publication////////////////////////////////////
def user_can_access_publication(user, publication) -> bool:
    """
    Returns True if the user can access the given publication
    based on visible features in their active subscription plan.
    """
    if not getattr(settings, 'SUBSCRIPTION_REQUIRED', True):
        return True

    if not user or not user.is_authenticated:
        return False

    now = timezone.now()

    # --------------------------------------------------
    # Get active CUSTOMER subscription
    # --------------------------------------------------

    # subscription = (
    #     CustomerSubscription.objects
    #         .select_related("plan")
    #         .filter(
    #         user=user,
    #         status="active",
    #         starts_at__lte=now,
    #     )
    #         .filter(
    #         Q(ends_at__isnull=True) | Q(ends_at__gte=now)
    #     )
    #         .first()
    # )

    subscription = _get_active_subscription(user)


    if not subscription:
        return False

    plan = subscription.plan
    #print(f"52 - plan: {plan}")

    # --------------------------------------------------
    # Feature-based access (visible == True only)
    # --------------------------------------------------
    # Newsletters are a research_category, not a research_type.
    # All other publications are matched by research_type.
    if publication.research_category == 'Newsletters':
        publication_type = 'Newsletters'
    else:
        publication_type = publication.research_type

    for feature in plan.features or []:
        if (
                feature.get("name") == publication_type
                and feature.get("visible") is True
        ):
            return True

    return False


#///////////////////////////////////////////active_subscription_q///////////////////////////////////////////////////////

ACTIVE_STATUS = "active"  # do NOT move this yet

def active_subscription_q():
    """
    Canonical definition of an active subscription.
    Scoped to the subscription app only.
    """
    now = timezone.now()
    return Q(
        status=ACTIVE_STATUS
    ) & (
                   Q(ends_at__isnull=True) |
                   Q(ends_at__gte=now)
           )


#////////////////////////////////////////////////////get_upgrade_recommendation/////////////////////////////
def get_upgrade_recommendation(user, publication):
    """
    Returns:
    {
        "current_plan": SubscriptionPlan | None,
        "required_plan": SubscriptionPlan | None
    }
    """

    if not user or not user.is_authenticated:
        return {"current_plan": None, "required_plan": None}

    now = timezone.now()

    # ---------------------------------------
    # 1️⃣ Get active subscription
    # ---------------------------------------
    subscription = _get_active_subscription(user)


    # subscription = (
    #     CustomerSubscription.objects
    #         .select_related("plan")
    #         .filter(
    #         user=user,
    #         status="active",
    #         starts_at__lte=now,
    #     )
    #         .filter(
    #         Q(ends_at__isnull=True) | Q(ends_at__gte=now)
    #     )
    #         .first()
    # )

    if not subscription:
        return {"current_plan": None, "required_plan": None}

    current_plan = subscription.plan
    publication_type = publication.research_type

    # ---------------------------------------
    # 2️⃣ Find lowest plan that contains feature
    # ---------------------------------------
    eligible_plans = (
        SubscriptionPlan.objects
            .filter(
            plan_type=current_plan.plan_type,
            is_active=True,
        )
            .order_by("display_order", "price_fcfa")
    )

    required_plan = None

    for plan in eligible_plans:
        for feature in plan.features or []:
            if (
                    feature.get("name") == publication_type
                    and feature.get("visible") is True
            ):
                required_plan = plan
                break

        if required_plan:
            break

    # ---------------------------------------
    # 3️⃣ Only suggest upgrade if it’s higher
    # ---------------------------------------
    if required_plan and required_plan.display_order <= current_plan.display_order:
        required_plan = None

    return {
        "current_plan": current_plan,
        "required_plan": required_plan,
    }
