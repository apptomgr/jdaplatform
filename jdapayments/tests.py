from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from jdapayments.models import Payment
from jdapayments.services import reprocess_payment
from jdasubscriptions.billing import BILLING_PERIOD_DELTA
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription, SubscriptionPlan

User = get_user_model()


class ReprocessPaymentTests(TestCase):
    """
    reprocess_payment is a live Django admin action ("Reprocess selected
    payments" on the Payment admin page), not dead code — it's the manual
    fallback staff use to recover a stuck payment when the browser-redirect
    activation flow never completes. It previously had the same missing
    ends_at bug that paystack_callback had before that was fixed elsewhere
    this session; this locks in the fix.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="reprocess_test_user", email="reprocess_test@example.com"
        )

    def _plan(self, billing_period, plan_type="customer", code_suffix=""):
        return SubscriptionPlan.objects.create(
            code=f"reprocess_test_plan_{billing_period}{code_suffix}",
            name=f"Reprocess Test Plan {billing_period}{code_suffix}",
            plan_type=plan_type,
            billing_period=billing_period,
            price_fcfa=1000,
            features=[],
            is_active=True,
        )

    def test_sets_ends_at_for_customer_subscription(self):
        plan = self._plan("quarterly", code_suffix="_customer")
        draft = CustomerSubscription.objects.create(
            user=self.user, plan=plan, status="draft", starts_at=None, ends_at=None
        )
        payment = Payment.objects.create(
            user=self.user,
            amount=1000,
            reference="reprocess_ref_customer",
            status="initialized",
            raw_response={
                "metadata": {
                    "subscription_id": draft.id,
                    "subscription_type": "customer",
                    "user_id": self.user.id,
                }
            },
        )

        before = timezone.now()
        result = reprocess_payment("reprocess_ref_customer")
        after = timezone.now()

        self.assertEqual(result, "Payment successfully reprocessed.")

        draft.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)
        self.assertGreaterEqual(draft.ends_at, before + BILLING_PERIOD_DELTA["quarterly"])
        self.assertLessEqual(draft.ends_at, after + BILLING_PERIOD_DELTA["quarterly"])
        self.assertEqual(payment.status, "success")

    def test_sets_ends_at_for_institution_subscription(self):
        plan = self._plan("yearly", plan_type="institution", code_suffix="_institution")
        draft = InstitutionSubscription.objects.create(
            user=self.user, plan=plan, status="draft", starts_at=None, ends_at=None
        )
        Payment.objects.create(
            user=self.user,
            amount=5000,
            reference="reprocess_ref_institution",
            status="initialized",
            raw_response={
                "metadata": {
                    "subscription_id": draft.id,
                    "subscription_type": "institution",
                    "user_id": self.user.id,
                }
            },
        )

        before = timezone.now()
        reprocess_payment("reprocess_ref_institution")
        after = timezone.now()

        draft.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)
        self.assertGreaterEqual(draft.ends_at, before + BILLING_PERIOD_DELTA["yearly"])
        self.assertLessEqual(draft.ends_at, after + BILLING_PERIOD_DELTA["yearly"])

    def test_expires_previous_active_subscription_and_sets_new_ends_at(self):
        plan = self._plan("monthly", code_suffix="_upgrade")
        now = timezone.now()
        old_active = CustomerSubscription.objects.create(
            user=self.user,
            plan=plan,
            status="active",
            starts_at=now - timedelta(days=10),
            ends_at=now + timedelta(days=20),
        )
        draft = CustomerSubscription.objects.create(
            user=self.user, plan=plan, status="draft", starts_at=None, ends_at=None
        )
        Payment.objects.create(
            user=self.user,
            amount=1000,
            reference="reprocess_ref_upgrade",
            status="initialized",
            raw_response={
                "metadata": {
                    "subscription_id": draft.id,
                    "subscription_type": "customer",
                    "user_id": self.user.id,
                }
            },
        )

        reprocess_payment("reprocess_ref_upgrade")

        old_active.refresh_from_db()
        draft.refresh_from_db()
        self.assertEqual(old_active.status, "expired")
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)

    def test_already_successful_payment_is_a_safe_noop(self):
        plan = self._plan("monthly", code_suffix="_noop")
        draft = CustomerSubscription.objects.create(
            user=self.user, plan=plan, status="draft", starts_at=None, ends_at=None
        )
        Payment.objects.create(
            user=self.user,
            amount=1000,
            reference="reprocess_ref_noop",
            status="success",
            raw_response={
                "metadata": {
                    "subscription_id": draft.id,
                    "subscription_type": "customer",
                    "user_id": self.user.id,
                }
            },
        )

        result = reprocess_payment("reprocess_ref_noop")

        self.assertEqual(result, "Payment already processed.")
        draft.refresh_from_db()
        self.assertEqual(draft.status, "draft")
        self.assertIsNone(draft.ends_at)

    def test_missing_subscription_metadata_is_reported_not_crashed(self):
        Payment.objects.create(
            user=self.user,
            amount=1000,
            reference="reprocess_ref_missing_meta",
            status="initialized",
            raw_response={"metadata": {}},
        )

        result = reprocess_payment("reprocess_ref_missing_meta")

        self.assertEqual(result, "Missing subscription metadata.")
