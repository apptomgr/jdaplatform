"""
Shared subscription-activation logic used by both the browser-redirect
callback (paystack_callback) and the Paystack webhook (paystack_webhook).

Deliberately session-independent: takes the already-verified Paystack
transaction data (the `data` dict from the Verify Transaction API), not a
Django request. A webhook call has no Django session/request.user at all,
so the previous design (paystack_callback scoping its subscription lookup
by request.user) couldn't be reused as-is by a webhook. This module is the
one place that logic lives, called from both.
"""

from dataclasses import dataclass
from typing import Optional

from django.utils import timezone

from jdapayments.models import Payment
from jdasubscriptions.billing import BILLING_PERIOD_DELTA
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription

STATUS_ACTIVATED = "activated"
STATUS_ALREADY_PROCESSED = "already_processed"
STATUS_INVALID_METADATA = "invalid_metadata"
STATUS_SUBSCRIPTION_NOT_FOUND = "subscription_not_found"
STATUS_UNKNOWN_SUBSCRIPTION_TYPE = "unknown_subscription_type"

_MODEL_BY_SUBSCRIPTION_TYPE = {
    "customer": CustomerSubscription,
    "institution": InstitutionSubscription,
}


@dataclass
class ActivationResult:
    status: str
    message: str
    subscription: Optional[object] = None


def activate_subscription_from_verified_payment(reference, verified_data):
    """
    verified_data is the `data` dict from Paystack's Verify Transaction API
    (GET /transaction/verify/{reference}). The caller must have already
    called Verify and confirmed verified_data["status"] == "success" —
    this function does not re-check that, it trusts the caller did.

    Idempotent: safe to call more than once with the same reference,
    whether that's the webhook and the browser callback racing on the same
    payment, or Paystack redelivering the same webhook event.
    """
    metadata = verified_data.get("metadata") or {}
    user_id = metadata.get("user_id")
    subscription_id = metadata.get("subscription_id")
    subscription_type = metadata.get("subscription_type")

    if not subscription_id or not subscription_type or not user_id:
        return ActivationResult(STATUS_INVALID_METADATA, "Invalid payment metadata.")

    # Created as "initialized", not "success" — only flipped to "success"
    # once activation below actually completes. Marking it "success" at
    # creation time would hide a partially-failed activation from
    # reprocess_payment, which explicitly skips rows already "success".
    payment, created = Payment.objects.get_or_create(
        reference=reference,
        defaults={
            "user_id": user_id,
            "amount": verified_data.get("amount", 0),
            "status": "initialized",
            "raw_response": verified_data,
        },
    )

    if not created and payment.status == "success":
        return ActivationResult(STATUS_ALREADY_PROCESSED, "Payment already processed.")

    if not created:
        # initialize_customer_payment / initialize_institution_payment
        # already created this row at checkout-initiation time (status
        # "initialized", amount = the raw plan price, raw_response = the
        # /transaction/initialize response). get_or_create's defaults never
        # apply to an existing row, so without this the row would keep
        # those stale initialize-time values forever — wrong amount, and a
        # raw_response with no metadata at all, which is exactly what
        # reprocess_payment needs to recover a stuck payment. Refresh it
        # with the real verified data now that we have it.
        payment.amount = verified_data.get("amount", 0)
        payment.raw_response = verified_data
        payment.user_id = user_id
        payment.save(update_fields=["amount", "raw_response", "user_id"])

    model = _MODEL_BY_SUBSCRIPTION_TYPE.get(subscription_type)
    if model is None:
        return ActivationResult(STATUS_UNKNOWN_SUBSCRIPTION_TYPE, "Unknown subscription type.")

    subscription = model.objects.filter(
        id=subscription_id,
        user_id=user_id,
        status="draft",
    ).first()

    if not subscription:
        return ActivationResult(
            STATUS_SUBSCRIPTION_NOT_FOUND,
            "Subscription not found or already activated.",
        )

    now = timezone.now()

    model.objects.filter(user_id=user_id, status="active").update(status="expired", ends_at=now)

    subscription.status = "active"
    subscription.starts_at = now
    subscription.ends_at = now + BILLING_PERIOD_DELTA[subscription.plan.billing_period]
    subscription.paystack_reference = reference
    subscription.paystack_status = "success"
    subscription.save()

    payment.status = "success"
    payment.save(update_fields=["status"])

    return ActivationResult(STATUS_ACTIVATED, "Subscription activated successfully.", subscription=subscription)
