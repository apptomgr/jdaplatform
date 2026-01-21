from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings

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

    class Meta:
        ordering = ["display_order", "price_fcfa"]
        verbose_name_plural = "SubscriptionPlan"

    def __str__(self):
        return f"{self.name} ({self.billing_period})"

# class SubscriptionPlan(models.Model):
#     """
#     Defines a purchasable subscription plan
#     """
#
#     PLAN_TYPE_CHOICES = (
#         ("customer", "Customer"),
#         ("institution", "Institution"),
#     )
#
#     BILLING_PERIOD_CHOICES = (
#         ("monthly", "Monthly"),
#         ("yearly", "Yearly"),
#     )
#
#     code = models.SlugField(max_length=50, unique=True, help_text="Internal identifier (e.g. akwaba_monthly)")
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default="customer")
#     billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES)
#     price_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
#     features = models.ManyToManyField("PlanFeature",blank=True,related_name="plans")
#     is_active = models.BooleanField(default=True)
#     display_order = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ["display_order", "price_fcfa"]
#         verbose_name_plural = "SubscriptionPlan"
#
#     def __str__(self):
#         return f"{self.name} ({self.billing_period})"


# #////////////////////////////////////////////////PlanFeature//////////////////////////////////////////
# from django.db import models
#
# class PlanFeature(models.Model):
#     """
#     A single feature that can be attached to subscription plans
#     """
#     code = models.SlugField(max_length=50, unique=True, help_text="Internal identifier (e.g. research_notes)")
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     display_order = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         ordering = ["display_order", "name"]
#         verbose_name_plural = "PlanFeature"
#
#     def __str__(self):
#         return self.name


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
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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

# class UserSubscription(models.Model):
#     STATUS_CHOICES = (
#         ("pending", "Pending"),
#         ("active", "Active"),
#         ("expired", "Expired"),
#         ("cancelled", "Cancelled"),
#     )
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="subscriptions_OLD")
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="user_subscriptions")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     start_date = models.DateTimeField(null=True, blank=True)
#     end_date = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def activate(self):
#         self.status = "active"
#         self.start_date = timezone.now()
#         self.save()
#
#     class Meta:
#         #ordering = ["display_order", "price_fcfa"]
#         verbose_name_plural = 'UserSubscription'
#
#     def __str__(self):
#         return f"{self.user} → {self.plan} ({self.status})"
#
#
# #//////////////////////////////////////////////CustomerSubscription/////////////////////////////////////////////////////
# class CustomerSubscription(models.Model):
#     """
#     Links a user to a selected subscription plan
#     """
#     STATUS_CHOICES = (
#         ("pending", "Pending"),
#         ("active", "Active"),
#         ("expired", "Expired"),
#         ("cancelled", "Cancelled"),
#     )
#
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions_OLD")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     start_date = models.DateField(null=True, blank=True)
#     end_date = models.DateField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         #ordering = ["display_order", "price_fcfa"]
#         verbose_name_plural = 'CustomerSubscription'
#
#     def __str__(self):
#         return f"{self.user} → {self.plan}"
#

# from django.db import models
#
# class SubscriptionType(models.TextChoices):
#     CUSTOMER = 'customer', 'Customer'
#     INSTITUTION = 'institution', 'Institution'
#
# class SubscriptionPlan(models.Model):
#     name = models.CharField(max_length=100)
#     plan_type = models.CharField(
#         max_length=20,
#         choices=SubscriptionType.choices,
#         default=SubscriptionType.CUSTOMER
#     )
#     monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
#     yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)
#     sort_order = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         ordering = ["sort_order", "name"]
#
#     def __str__(self):
#         return f"{self.name} ({self.plan_type})"
