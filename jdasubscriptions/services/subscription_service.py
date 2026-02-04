import requests
import logging
from dataclasses import dataclass
from django.conf import settings
from django.utils import timezone

from jdapayments.models import Payment
from jdasubscriptions.models import (
    CustomerSubscription,
    InstitutionSubscription,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    success: bool
    message: str
    subscription: object | None = None
    payment: Payment | None = None


def process_successful_payment(reference: str) -> ProcessResult:
    """
    Single source of truth for activating subscriptions from Paystack payments
    """

    # --------------------------------------------------
    # 1️⃣ Verify transaction with Paystack
    # --------------------------------------------------
    verify_url = f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(verify_url, headers=headers, timeout=15)
        result = response.json()
    except Exception:
        logger.exception("Paystack verification failed")
        return ProcessResult(False, "Paystack verification error")

    if not result.get("status"):
        return ProcessResult(False, "Invalid Paystack verification response")

    data = result.get("data") or {}
    metadata = data.get("metadata") or {}

    if data.get("status") != "success":
        return ProcessResult(False, "Payment not successful")

    # --------------------------------------------------
    # 2️⃣ Idempotent payment handling
    # --------------------------------------------------
    payment, created = Payment.objects.get_or_create(
        reference=reference,
        defaults={
            "user_id": metadata.get("user_id"),
            "amount": data.get("amount", 0) / 100,  # XOF safe
            "status": "success",
            "raw_response": data,
        },
    )

    if not created and payment.status == "success":
        return ProcessResult(
            True,
            "Payment already processed",
            payment=payment,
        )

    # --------------------------------------------------
    # 3️⃣ Extract subscription metadata
    # --------------------------------------------------
    subscription_id = metadata.get("subscription_id")
    subscription_type = metadata.get("subscription_type")

    if not subscription_id or not subscription_type:
        return ProcessResult(False, "Missing subscription metadata")

    now = timezone.now()

    # --------------------------------------------------
    # 4️⃣ Activate correct subscription
    # --------------------------------------------------
    try:
        if subscription_type == "customer":
            subscription = CustomerSubscription.objects.get(
                id=subscription_id,
                status="draft",
            )

            CustomerSubscription.objects.filter(
                user=subscription.user,
                status="active",
            ).update(status="expired", ends_at=now)

        elif subscription_type == "institution":
            subscription = InstitutionSubscription.objects.get(
                id=subscription_id,
                status="draft",
            )

            InstitutionSubscription.objects.filter(
                user=subscription.user,
                status="active",
            ).update(status="expired", ends_at=now)

        else:
            return ProcessResult(False, "Unknown subscription type")

    except (CustomerSubscription.DoesNotExist, InstitutionSubscription.DoesNotExist):
        return ProcessResult(
            True,
            "Subscription already processed or missing",
            payment=payment,
        )

    # --------------------------------------------------
    # 5️⃣ Finalize subscription + payment
    # --------------------------------------------------
    subscription.status = "active"
    subscription.starts_at = now
    subscription.paystack_reference = reference
    subscription.paystack_status = "success"
    subscription.save()

    payment.status = "success"
    payment.save()

    return ProcessResult(
        True,
        "Subscription activated successfully",
        subscription=subscription,
        payment=payment,
    )




