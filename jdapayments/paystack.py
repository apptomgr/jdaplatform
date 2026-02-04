import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

if not getattr(settings, "PAYSTACK_SECRET_KEY", None):
    raise RuntimeError(
        "PAYSTACK_SECRET_KEY is not set. "
        "Check your .env and settings.py configuration."
    )

HEADERS = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


def initialize_payment(email, amount, callback_url, metadata=None):
    """
    Initialize a Paystack transaction
    Amount must be in kobo (integer)
    """
    payload = {
        "email": email,
        "amount": amount,
        "callback_url": callback_url,
        "metadata": metadata or {},
    }

    response = requests.post(
        f"{PAYSTACK_BASE_URL}/transaction/initialize",
        json=payload,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()


def verify_payment(reference):
    """
    Verify a Paystack transaction
    """
    response = requests.get(
        f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
        headers=HEADERS,
        timeout=15,
    )

    return response.json()
