from django.utils import timezone
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription
#from jdasubscriptions.services.access_services import (
#    user_has_active_subscription,
#    user_can_access_publication,
#)


def user_has_active_subscription(user):
    now = timezone.now()
    return (
            CustomerSubscription.objects.filter(user=user, status="active", starts_at__lte=now,).filter(ends_at__isnull=True).exists() or
            InstitutionSubscription.objects.filter(user=user, status="active", starts_at__lte=now,).filter(ends_at__isnull=True).exists()
    )




#///////////////////////////////////user_can_access_publication////////////////////////////////////
def user_can_access_publication(user, publication) -> bool:
    """
    Returns True if the user can access the given publication
    based on visible features in their active subscription plan.
    """

    if not user or not user.is_authenticated:
        return False

    now = timezone.now()

    # --------------------------------------------------
    # Get active CUSTOMER subscription
    # --------------------------------------------------
    subscription = (
        CustomerSubscription.objects
            .select_related("plan")
            .filter(
            user=user,
            status="active",
            starts_at__lte=now,
        )
            .filter(
            ends_at__isnull=True
        )
            .first()
    )

    #print(f"48 - plan: {subscription}")

    if not subscription:
        return False

    plan = subscription.plan
    #print(f"52 - plan: {plan}")

    # --------------------------------------------------
    # Gold = unrestricted access
    # --------------------------------------------------
    if plan.code.lower() == "akwaba-gold":
        return True

    # --------------------------------------------------
    # Feature-based access (visible == True only)
    # --------------------------------------------------
    publication_type = publication.research_type
    #print(f"63: publication_type - {publication_type}")

    for feature in plan.features or []:
        #print(f"66: feature - {plan.features or []}")
        print(f"67: feature name - {feature.get('name')}")
        if (
                feature.get("name") == publication_type
                and feature.get("visible") is True
        ):
            return True

    return False


# def user_has_active_subscription(user):
#     if not user.is_authenticated:
#
#         return False
#
#     return (
#             CustomerSubscription.objects.filter(user=user, status="active").exists()
#             or InstitutionSubscription.objects.filter(user=user, status="active").exists()
#     )

#///////////////////////////////////////////active_subscription_q///////////////////////////////////////////////////////
from django.db.models import Q
from django.utils import timezone

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

