import re
import unicodedata

from django.conf import settings
from django.utils import timezone
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription, SubscriptionPlan
from django.db.models import Q

# Maps research_type values (stored on PublicationModel) to the display-friendly
# feature names used in SubscriptionPlan.features JSON. Only entries that differ
# need an explicit mapping; identical names resolve via the .get() fallback.
RESEARCH_TYPE_TO_FEATURE = {
    "Recommendation":             "Recommendations",
    "IPO Analysis":               "IPO Analysis",
    "Quarterly Results":          "Quarterly Results Commentary",
    "Half Year Results":          "Half Year Results Commentary",
    "Semi-annual Results":        "Half Year Results Commentary",
    "Annual Results":             "Annual Results Commentary",
    "Shareholder Meeting Feedback": "General Meetings Commentary",
    "Research Notes":             "Research Notes",
    "Economic Notes":             "Economic Notes",
    "Stock Pitch":                "Stock Pitch",
}

_WHITESPACE_RE = re.compile(r'\s+')


def _normalize_for_match(text):
    """Case-insensitive, accent-insensitive, whitespace-collapsed comparison key."""
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = _WHITESPACE_RE.sub(' ', text.strip())
    return text.lower()


def _is_stock_opinion_subject(subject) -> bool:
    """
    A publication is treated as a Stock Opinion piece if its subject starts
    with "AVIS SUR" — any case, accents, or repeated/leading whitespace —
    regardless of what follows or what research_type it's filed under.
    """
    return _normalize_for_match(subject).startswith('avis sur')


def _plan_grants_publication(features, publication_type, publication) -> bool:
    """
    Shared by user_can_access_publication and get_upgrade_recommendation so
    both agree on what a given plan's features actually grant.
    """
    # --- Existing feature check, unchanged ---
    matched_feature = None
    for feature in features or []:
        if feature.get("name") == publication_type and feature.get("visible") is True:
            matched_feature = feature
            break

    if matched_feature is None:
        return False

    # --- Subtractive layer, applied only after the existing check above
    # already granted access. This can only turn a True into a False —
    # it can never grant access the check above denied. A plan's matched
    # "Recommendations" feature still denies a Stock Opinion piece if that
    # plan's own data lists "Stock Opinion" in sub_items_excluded. Read
    # entirely from the feature dict being evaluated — no plan is
    # special-cased by name, so this stays correct as plan data changes. ---
    if matched_feature.get("name") == "Recommendations" and _is_stock_opinion_subject(publication.subject):
        if "Stock Opinion" in (matched_feature.get("sub_items_excluded") or []):
            return False

    return True

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
    # All other publications are matched via RESEARCH_TYPE_TO_FEATURE so that
    # display-friendly feature names in plan JSON resolve to research_type values.
    if publication.research_category == 'Newsletters':
        publication_type = 'Newsletters'
    else:
        publication_type = RESEARCH_TYPE_TO_FEATURE.get(
            publication.research_type, publication.research_type
        )

    return _plan_grants_publication(plan.features, publication_type, publication)


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
    publication_type = RESEARCH_TYPE_TO_FEATURE.get(
        publication.research_type, publication.research_type
    )

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
        if _plan_grants_publication(plan.features, publication_type, publication):
            required_plan = plan
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
