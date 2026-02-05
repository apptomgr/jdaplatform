from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


User = settings.AUTH_USER_MODEL

#////////////////////////////////////////////////SubscriptionPlan//////////////////////////////////////////
class SubscriptionPlan(models.Model):
    PLAN_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("institution", "Institution"),
    )

    BILLING_PERIOD_CHOICES = (
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    )

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES)
    price_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paystack_reference = models.CharField(max_length=100, blank=True)
    paystack_status = models.CharField(max_length=50, blank=True)


    class Meta:
        ordering = ["display_order", "price_fcfa"]
        verbose_name_plural = "SubscriptionPlan"

    def __str__(self):
        return f"{self.name} ({self.billing_period})"


# #///////////////////////////////////////////////CustomerSubscription//////////////////////////////////////////////
class CustomerSubscription(models.Model):
    """
    A draft or active subscription for a customer user
    """
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Expired"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions_OLD")
    plan = models.ForeignKey("SubscriptionPlan", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paystack_reference = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    paystack_status = models.CharField(max_length=50, blank=True)




    class Meta:
        #unique_together = ("user", "status")
        verbose_name_plural = "CustomerSubscription"

    def is_active(self):
        now = timezone.now()
        return (
                self.status == "active"
                and self.starts_at <= now
                and (self.ends_at is None or self.ends_at >= now)
        )


    def __str__(self):
        return f"{self.user} → {self.plan} ({self.status})"


# #///////////////////////////////////////////////InstitutionSubscription//////////////////////////////////////////////
class InstitutionSubscription(models.Model):
    """
    Subscription for institution users (no Institution model required)
    """
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Expired"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="institution_subscriptions"
    )

    plan = models.ForeignKey(
        "SubscriptionPlan",
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paystack_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)
    paystack_status = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Institution Subscriptions"

    def is_active(self):
        now = timezone.now()
        return (
                self.status == "active"
                and self.starts_at
                and self.starts_at <= now
                and (self.ends_at is None or self.ends_at >= now)
        )

    def __str__(self):
        return f"Institution → {self.user} → {self.plan} ({self.status})"


# #///////////////////////////////////////////////UserSubscription//////////////////////////////////////////////
# jdasubscriptions/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserSubscription(models.Model):
    """
    Represents an active or past subscription for a user
    """

    STATUS_CHOICES = (
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        "SubscriptionPlan",
        on_delete=models.PROTECT,
        related_name="user_subscriptions",
    )

    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["end_date"]),
        ]

    def __str__(self):
        return f"{self.user} → {self.plan} ({self.status})"

    @property
    def is_active(self):
        return (
                self.status == "active"
                and self.end_date >= timezone.now()
        )

