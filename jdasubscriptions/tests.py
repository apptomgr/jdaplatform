from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django.utils import timezone

from jdasubscriptions.billing import BILLING_PERIOD_DELTA
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription, SubscriptionPlan
from jdasubscriptions.services.access_services import user_has_active_subscription, _get_active_subscription

User = get_user_model()


def _make_plan(billing_period, code_suffix=""):
    return SubscriptionPlan.objects.create(
        code=f"test_plan_{billing_period}{code_suffix}",
        name=f"Test Plan {billing_period}{code_suffix}",
        plan_type="customer",
        billing_period=billing_period,
        price_fcfa=1000,
        features=[],
        is_active=True,
    )


class BillingPeriodDeltaTests(TestCase):
    """
    Sanity pass: the delta table must cover exactly the billing periods
    SubscriptionPlan actually offers, and each period must be strictly
    longer than the shorter ones (quarterly != monthly's interval, etc.)
    """

    def test_covers_every_billing_period_choice(self):
        choices = {c[0] for c in SubscriptionPlan.BILLING_PERIOD_CHOICES}
        self.assertEqual(choices, set(BILLING_PERIOD_DELTA.keys()))

    def test_periods_are_correctly_ordered(self):
        now = timezone.now()
        monthly_end = now + BILLING_PERIOD_DELTA["monthly"]
        quarterly_end = now + BILLING_PERIOD_DELTA["quarterly"]
        yearly_end = now + BILLING_PERIOD_DELTA["yearly"]

        self.assertLess(monthly_end, quarterly_end)
        self.assertLess(quarterly_end, yearly_end)
        # Quarterly must not collapse to the same interval as monthly.
        self.assertGreaterEqual((quarterly_end - now).days, 89)
        self.assertGreaterEqual((yearly_end - now).days, 365)


class ExpiryCheckTests(TestCase):
    """
    Reproduces the diagnosis: confirms user_has_active_subscription
    correctly denies access once ends_at is populated and in the past,
    across every billing period, at various subscription ages.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="expiry_test_user", email="expiry_test@example.com")

    def test_denies_access_when_ends_at_is_in_the_past(self):
        now = timezone.now()
        for billing_period in ("monthly", "quarterly", "yearly"):
            plan = _make_plan(billing_period)
            sub = CustomerSubscription.objects.create(
                user=self.user,
                plan=plan,
                status="active",
                starts_at=now - timedelta(days=400),
                ends_at=now - timedelta(days=5),
            )
            self.assertFalse(
                user_has_active_subscription(self.user),
                f"{billing_period}: expired subscription should not grant access",
            )
            sub.delete()

    def test_grants_access_when_ends_at_is_in_the_future(self):
        now = timezone.now()
        plan = _make_plan("monthly", "_future")
        CustomerSubscription.objects.create(
            user=self.user,
            plan=plan,
            status="active",
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=29),
        )
        self.assertTrue(user_has_active_subscription(self.user))

    def test_null_ends_at_is_treated_as_never_expiring(self):
        """
        Documents the mechanism behind the original bug: a null ends_at is
        legitimate for complimentary/lifetime subscriptions, so the query
        itself is correct — the bug was that paid subscriptions never got
        ends_at populated in the first place (fixed separately, in
        paystack_callback and the backfill command).
        """
        now = timezone.now()
        plan = _make_plan("monthly", "_null")
        CustomerSubscription.objects.create(
            user=self.user,
            plan=plan,
            status="active",
            starts_at=now - timedelta(days=400),
            ends_at=None,
        )
        self.assertTrue(user_has_active_subscription(self.user))


class PaystackCallbackActivationTests(TestCase):
    """
    Exercises the real activation path (the only one wired into urls.py)
    with a stubbed Paystack verification response, confirming ends_at is
    now computed from the plan's billing_period rather than left null.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="activation_test_user",
            email="activation_test@example.com",
            password="testpass123",
        )
        self.client.force_login(self.user)

    def _stub_verify_response(self, subscription, subscription_type):
        return {
            "status": True,
            "data": {
                "status": "success",
                "amount": 100000,
                "reference": "test_ref_123",
                "metadata": {
                    "subscription_id": subscription.id,
                    "subscription_type": subscription_type,
                    "user_id": self.user.id,
                },
            },
        }

    @patch("jdasubscriptions.views.requests.get")
    def test_customer_activation_sets_ends_at_from_billing_period(self, mock_get):
        plan = _make_plan("quarterly", "_activation")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")

        mock_get.return_value.json.return_value = self._stub_verify_response(draft, "customer")

        before = timezone.now()
        response = self.client.get(reverse("jdasubscriptions:paystack_callback"), {"reference": "test_ref_123"})
        after = timezone.now()

        draft.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)
        self.assertGreaterEqual(draft.ends_at, before + BILLING_PERIOD_DELTA["quarterly"])
        self.assertLessEqual(draft.ends_at, after + BILLING_PERIOD_DELTA["quarterly"])

    @patch("jdasubscriptions.views.requests.get")
    def test_institution_activation_sets_ends_at_from_billing_period(self, mock_get):
        plan = SubscriptionPlan.objects.create(
            code="test_inst_plan_yearly",
            name="Test Institution Plan",
            plan_type="institution",
            billing_period="yearly",
            price_fcfa=5000,
            features=[],
            is_active=True,
        )
        draft = InstitutionSubscription.objects.create(user=self.user, plan=plan, status="draft")

        mock_get.return_value.json.return_value = self._stub_verify_response(draft, "institution")

        before = timezone.now()
        self.client.get(reverse("jdasubscriptions:paystack_callback"), {"reference": "test_ref_123"})

        draft.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)
        self.assertGreaterEqual(draft.ends_at, before + BILLING_PERIOD_DELTA["yearly"] - timedelta(minutes=1))


class BackfillCommandTests(TestCase):
    """
    Runs entirely against Django's isolated test database — never touches
    the real dev DB. Confirms dry-run classification and that --apply only
    ever writes OK rows, per the explicit decision that ALREADY_EXPIRED
    rows require manual customer notification first.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="backfill_test_user", email="backfill_test@example.com")
        self.now = timezone.now()

    def _sub(self, billing_period="monthly", starts_at=None, code_suffix=""):
        plan = _make_plan(billing_period, code_suffix)
        return CustomerSubscription.objects.create(
            user=self.user,
            plan=plan,
            status="active",
            starts_at=starts_at,
            ends_at=None,
        )

    def test_dry_run_classifies_without_writing(self):
        ok_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_ok")
        expired_sub = self._sub(starts_at=self.now - timedelta(days=400), code_suffix="_expired")
        ambiguous_sub = self._sub(starts_at=None, code_suffix="_ambiguous")

        out = StringIO()
        call_command("backfill_subscription_end_dates", stdout=out)
        output = out.getvalue()

        self.assertIn("OK", output)
        self.assertIn("ALREADY_EXPIRED", output)
        self.assertIn("AMBIGUOUS", output)
        self.assertIn("Dry run only", output)

        for sub in (ok_sub, expired_sub, ambiguous_sub):
            sub.refresh_from_db()
            self.assertIsNone(sub.ends_at, "dry run must never write")

    def test_apply_writes_only_ok_rows(self):
        ok_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_ok2")
        expired_sub = self._sub(starts_at=self.now - timedelta(days=400), code_suffix="_expired2")
        ambiguous_sub = self._sub(starts_at=None, code_suffix="_ambiguous2")

        out = StringIO()
        call_command("backfill_subscription_end_dates", "--apply", stdout=out)

        ok_sub.refresh_from_db()
        expired_sub.refresh_from_db()
        ambiguous_sub.refresh_from_db()

        self.assertIsNotNone(ok_sub.ends_at)
        self.assertIsNone(expired_sub.ends_at, "ALREADY_EXPIRED must never be auto-applied")
        self.assertIsNone(ambiguous_sub.ends_at, "AMBIGUOUS must never be auto-applied")

    def test_unrecognized_billing_period_is_ambiguous_not_guessed(self):
        plan = SubscriptionPlan.objects.create(
            code="test_plan_biweekly",
            name="Test Plan biweekly",
            plan_type="customer",
            billing_period="monthly",  # valid at model level; we corrupt it below
            price_fcfa=1000,
            features=[],
            is_active=True,
        )
        SubscriptionPlan.objects.filter(pk=plan.pk).update(billing_period="biweekly")
        plan.refresh_from_db()

        sub = CustomerSubscription.objects.create(
            user=self.user,
            plan=plan,
            status="active",
            starts_at=self.now - timedelta(days=1),
            ends_at=None,
        )

        out = StringIO()
        call_command("backfill_subscription_end_dates", "--apply", stdout=out)

        sub.refresh_from_db()
        self.assertIsNone(sub.ends_at)
        self.assertIn("AMBIGUOUS", out.getvalue())
        self.assertIn("unrecognized billing_period", out.getvalue())
