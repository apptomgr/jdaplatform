import uuid
import json
import hmac
import hashlib
import requests

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from .models import Payment


def payment_page(request):
    return render(request, "paystack_test/payment.html")


def start_payment(request):
    email = request.POST.get("email")
    amount_fcfa = 5000

    reference = str(uuid.uuid4())

    payment = Payment.objects.create(email=email, amount=amount_fcfa * 100, reference=reference,)

    payload = {
        "email": email,
        "amount": payment.amount,
        "reference": reference,
        "callback_url": request.build_absolute_uri(
            "/paystack/callback/"
        ),
        "currency": "XOF"
    }

    print(payload)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers,
        timeout=10
    )

    res = response.json()

    if res.get("status"):
        return redirect(res["data"]["authorization_url"])

    payment.status = "failed"
    payment.save()

    return render(request, "paystack_test/error.html", {"error": res})


def payment_callback(request):
    return render(request, "paystack_test/success.html")




@csrf_exempt
def paystack_webhook(request):
    signature = request.headers.get("x-paystack-signature")
    body = request.body

    computed = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if signature != computed:
        return HttpResponseForbidden("Invalid signature")

    payload = json.loads(body)

    if payload["event"] == "charge.success":
        reference = payload["data"]["reference"]

        Payment.objects.filter(
            reference=reference
        ).update(status="paid")

    return HttpResponse(status=200)
