from django.utils import timezone

from jdasubscriptions.models import (
    CustomerSubscription,
    InstitutionSubscription,
)


#//////////////////////////////////////////get_active_subscription////////////////////////////////
def get_active_subscription(user):
    """
    Returns the active subscription regardless of type.
    Institution takes priority over customer.
    """

    if not user or not user.is_authenticated:
        return None

    now = timezone.now()

    # Institution FIRST (priority)
    institution = (
            InstitutionSubscription.objects
            .filter(
                user=user,
                status="active",
                starts_at__lte=now
            )
            .filter(ends_at__isnull=True) |
            InstitutionSubscription.objects.filter(
                user=user,
                status="active",
                starts_at__lte=now,
                ends_at__gte=now
            )
    ).order_by("-created_at").first()

    if institution:
        return institution

    # Customer SECOND
    customer = (
            CustomerSubscription.objects
            .filter(
                user=user,
                status="active",
                starts_at__lte=now
            )
            .filter(ends_at__isnull=True) |
            CustomerSubscription.objects.filter(
                user=user,
                status="active",
                starts_at__lte=now,
                ends_at__gte=now
            )
    ).order_by("-created_at").first()

    if customer:
        return customer

    return None


def get_active_plan(user):
    subscription = get_active_subscription(user)
    return subscription.plan if subscription else None


def user_has_active_subscription(user):
    return get_active_subscription(user) is not None
