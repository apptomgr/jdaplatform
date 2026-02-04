from django.utils import timezone
from jdapayments.models import Payment
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription

def reprocess_payment(reference: str) -> str:
    """
    Idempotently reprocess a successful Paystack payment.
    Returns a human-readable result message.
    """

    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        return "Payment not found."

    if payment.status == "success":
        # Already processed — safe no-op
        return "Payment already processed."

    data = payment.raw_response or {}
    metadata = data.get("metadata") or {}

    subscription_id = metadata.get("subscription_id")
    subscription_type = metadata.get("subscription_type")

    if not subscription_id or not subscription_type:
        return "Missing subscription metadata."

    now = timezone.now()

    if subscription_type == "customer":
        subscription = CustomerSubscription.objects.filter(
            id=subscription_id,
            status="draft",
        ).first()

        if not subscription:
            return "Customer subscription already processed or missing."

        CustomerSubscription.objects.filter(
            user=subscription.user,
            status="active",
        ).update(status="expired", ends_at=now)

    elif subscription_type == "institution":
        subscription = InstitutionSubscription.objects.filter(
            id=subscription_id,
            status="draft",
        ).first()

        if not subscription:
            return "Institution subscription already processed or missing."

        InstitutionSubscription.objects.filter(
            user=subscription.user,
            status="active",
        ).update(status="expired", ends_at=now)

    else:
        return "Unknown subscription type."

    subscription.status = "active"
    subscription.starts_at = now
    subscription.paystack_reference = payment.reference
    subscription.paystack_status = "success"
    subscription.save()

    payment.status = "success"
    payment.save(update_fields=["status"])

    return "Payment successfully reprocessed."
