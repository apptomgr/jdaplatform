import csv
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command
from django.utils import timezone

from jdapayments.models import Payment
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

    @patch("jdapayments.paystack.requests.get")
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

    @patch("jdapayments.paystack.requests.get")
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


class PaystackWebhookTests(TestCase):
    """
    The server-to-server webhook — the reliable primary activation path,
    independent of the customer's browser completing a redirect back to
    paystack_callback. Covers signature verification, idempotency against
    duplicate delivery, ignoring irrelevant event types, and that the
    webhook and the browser callback can't double-activate the same
    payment when both fire for it.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="webhook_test_user",
            email="webhook_test@example.com",
            password="testpass123",
        )

    def _charge_success_payload(self, subscription, subscription_type, reference="webhook_test_ref"):
        return {
            "event": "charge.success",
            "data": {
                "status": "success",
                "amount": 100000,
                "reference": reference,
                "metadata": {
                    "subscription_id": subscription.id,
                    "subscription_type": subscription_type,
                    "user_id": self.user.id,
                },
            },
        }

    def _signed_post(self, payload):
        import hashlib
        import hmac
        import json

        from django.conf import settings

        raw_body = json.dumps(payload).encode("utf-8")
        signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"), raw_body, hashlib.sha512
        ).hexdigest()
        return self.client.post(
            reverse("jdasubscriptions:paystack_webhook"),
            data=raw_body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature,
        )

    def _stub_verify_response(self, payload):
        data = payload["data"]
        return {"status": True, "data": data}

    @patch("jdapayments.paystack.requests.get")
    def test_valid_signature_charge_success_activates_subscription(self, mock_get):
        plan = _make_plan("monthly", "_webhook_ok")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = self._charge_success_payload(draft, "customer", reference="webhook_ref_ok")
        mock_get.return_value.json.return_value = self._stub_verify_response(payload)

        before = timezone.now()
        response = self._signed_post(payload)
        after = timezone.now()

        self.assertEqual(response.status_code, 200)
        draft.refresh_from_db()
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(draft.ends_at)
        self.assertGreaterEqual(draft.ends_at, before + BILLING_PERIOD_DELTA["monthly"])
        self.assertLessEqual(draft.ends_at, after + BILLING_PERIOD_DELTA["monthly"])

        payment = Payment.objects.get(reference="webhook_ref_ok")
        self.assertEqual(payment.status, "success")

    @patch("jdapayments.paystack.requests.get")
    def test_refreshes_a_payment_row_pre_created_at_checkout_initiation(self, mock_get):
        """
        Found via a real end-to-end pass against real Paystack test-mode
        API calls, not by the mocked test suite: initialize_customer_payment
        / initialize_institution_payment already create the Payment row at
        checkout-initiation time (status "initialized", amount = the raw
        plan price, raw_response = the /transaction/initialize response —
        no metadata in it at all). get_or_create's defaults never apply to
        an existing row, so without refreshing it here, the row keeps those
        stale values forever: the wrong amount, and a raw_response
        reprocess_payment can't extract metadata from. This reproduces that
        exact real-world shape rather than the simplified "Payment doesn't
        exist yet" case the other tests use.
        """
        plan = _make_plan("monthly", "_webhook_preexisting_payment")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        reference = "webhook_ref_preexisting_payment"

        # Mirrors initialize_customer_payment's Payment.objects.update_or_create
        Payment.objects.create(
            user=self.user,
            amount=int(plan.price_fcfa),  # stale: raw price, not the verified subunit amount
            reference=reference,
            status="initialized",
            raw_response={
                "status": True,
                "message": "Authorization URL created",
                "data": {
                    "authorization_url": "https://checkout.paystack.com/fake",
                    "access_code": "fake_access_code",
                    "reference": reference,
                },
            },
        )

        payload = self._charge_success_payload(draft, "customer", reference=reference)
        payload["data"]["amount"] = 250000  # the real verified subunit amount
        mock_get.return_value.json.return_value = self._stub_verify_response(payload)

        response = self._signed_post(payload)

        self.assertEqual(response.status_code, 200)
        draft.refresh_from_db()
        self.assertEqual(draft.status, "active")

        payment = Payment.objects.get(reference=reference)
        self.assertEqual(payment.status, "success")
        self.assertEqual(payment.amount, 250000, "must be refreshed from the verified amount, not left stale")
        self.assertIn(
            "metadata", payment.raw_response,
            "raw_response must be refreshed to the verified data so reprocess_payment can read metadata from it",
        )

    def test_invalid_signature_is_rejected_without_touching_the_database(self):
        plan = _make_plan("monthly", "_webhook_badsig")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = self._charge_success_payload(draft, "customer", reference="webhook_ref_badsig")

        response = self.client.post(
            reverse("jdasubscriptions:paystack_webhook"),
            data=payload,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE="not-a-real-signature",
        )

        self.assertEqual(response.status_code, 403)
        draft.refresh_from_db()
        self.assertEqual(draft.status, "draft")
        self.assertFalse(Payment.objects.filter(reference="webhook_ref_badsig").exists())

    def test_missing_signature_header_is_rejected(self):
        plan = _make_plan("monthly", "_webhook_nosig")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = self._charge_success_payload(draft, "customer", reference="webhook_ref_nosig")

        response = self.client.post(
            reverse("jdasubscriptions:paystack_webhook"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("jdapayments.paystack.requests.get")
    def test_duplicate_delivery_only_activates_once(self, mock_get):
        plan = _make_plan("monthly", "_webhook_dup")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = self._charge_success_payload(draft, "customer", reference="webhook_ref_dup")
        mock_get.return_value.json.return_value = self._stub_verify_response(payload)

        first = self._signed_post(payload)
        draft.refresh_from_db()
        first_ends_at = draft.ends_at

        second = self._signed_post(payload)
        draft.refresh_from_db()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(draft.ends_at, first_ends_at, "redelivery must not recompute/shift ends_at")
        self.assertEqual(Payment.objects.filter(reference="webhook_ref_dup").count(), 1)

    def test_non_charge_success_event_is_acknowledged_and_ignored(self):
        plan = _make_plan("monthly", "_webhook_otherevent")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = {
            "event": "charge.failed",
            "data": {
                "status": "failed",
                "reference": "webhook_ref_otherevent",
                "metadata": {
                    "subscription_id": draft.id,
                    "subscription_type": "customer",
                    "user_id": self.user.id,
                },
            },
        }

        response = self._signed_post(payload)

        self.assertEqual(response.status_code, 200)
        draft.refresh_from_db()
        self.assertEqual(draft.status, "draft")
        self.assertFalse(Payment.objects.filter(reference="webhook_ref_otherevent").exists())

    @patch("jdapayments.paystack.requests.get")
    def test_webhook_then_browser_callback_do_not_double_activate(self, mock_get):
        """
        The scenario this whole feature exists for: both paths fire for
        the same payment (webhook arrives, then the browser also completes
        its redirect, or vice versa). Only the first to arrive should
        actually activate anything.
        """
        plan = _make_plan("monthly", "_webhook_then_callback")
        draft = CustomerSubscription.objects.create(user=self.user, plan=plan, status="draft")
        payload = self._charge_success_payload(draft, "customer", reference="webhook_ref_race")
        mock_get.return_value.json.return_value = self._stub_verify_response(payload)

        webhook_response = self._signed_post(payload)
        draft.refresh_from_db()
        ends_at_after_webhook = draft.ends_at

        self.assertEqual(webhook_response.status_code, 200)
        self.assertEqual(draft.status, "active")
        self.assertIsNotNone(ends_at_after_webhook)

        self.client.force_login(self.user)
        callback_response = self.client.get(
            reverse("jdasubscriptions:paystack_callback"), {"reference": "webhook_ref_race"}
        )

        draft.refresh_from_db()
        self.assertEqual(callback_response.status_code, 302)
        self.assertEqual(draft.status, "active")
        self.assertEqual(draft.ends_at, ends_at_after_webhook, "browser callback must not re-activate")
        self.assertEqual(Payment.objects.filter(reference="webhook_ref_race").count(), 1)

    @patch("jdapayments.paystack.requests.get")
    def test_subscription_not_found_is_acknowledged_but_left_recoverable(self, mock_get):
        """
        A data problem (bad/stale metadata) isn't something Paystack
        retrying will fix, so this still returns 200 — but the Payment
        must stay "initialized", not "success", so it surfaces for the
        admin "Reprocess selected payments" action rather than being
        silently invisible to it.
        """
        payload = {
            "event": "charge.success",
            "data": {
                "status": "success",
                "amount": 100000,
                "reference": "webhook_ref_notfound",
                "metadata": {
                    "subscription_id": 999999,
                    "subscription_type": "customer",
                    "user_id": self.user.id,
                },
            },
        }
        mock_get.return_value.json.return_value = self._stub_verify_response(payload)

        response = self._signed_post(payload)

        self.assertEqual(response.status_code, 200)
        payment = Payment.objects.get(reference="webhook_ref_notfound")
        self.assertEqual(payment.status, "initialized")


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

    def test_explicit_dry_run_flag_does_not_error_and_does_not_write(self):
        """
        The docstring advertises `--dry-run` as an explicit no-op alias for
        the default (no-flag) behavior. It must actually be a recognized
        argparse flag, not just documented — this caught a real gap where
        the flag was described but never implemented.
        """
        ok_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_explicit_dry_run")

        out = StringIO()
        call_command("backfill_subscription_end_dates", "--dry-run", stdout=out)

        ok_sub.refresh_from_db()
        self.assertIsNone(ok_sub.ends_at)
        self.assertIn("Dry run only", out.getvalue())

    def test_dry_run_overrides_apply_when_both_passed(self):
        """Safety net: --apply --dry-run together must not write anything."""
        ok_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_both_flags")

        call_command("backfill_subscription_end_dates", "--apply", "--dry-run", stdout=StringIO())

        ok_sub.refresh_from_db()
        self.assertIsNone(ok_sub.ends_at, "--dry-run must override --apply when both are passed")

    def test_apply_writes_ok_and_already_expired_but_not_ambiguous(self):
        """
        Per Ivan's revised decision (Paystack still in test mode, most of
        these were never real paid transactions): --apply now auto-expires
        ALREADY_EXPIRED rows too, with no individual notification. Only
        AMBIGUOUS (and EXCLUDED, covered separately) stay untouched.
        """
        ok_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_ok2")
        expired_sub = self._sub(starts_at=self.now - timedelta(days=400), code_suffix="_expired2")
        ambiguous_sub = self._sub(starts_at=None, code_suffix="_ambiguous2")

        out = StringIO()
        call_command("backfill_subscription_end_dates", "--apply", stdout=out)

        ok_sub.refresh_from_db()
        expired_sub.refresh_from_db()
        ambiguous_sub.refresh_from_db()

        self.assertIsNotNone(ok_sub.ends_at)
        self.assertIsNotNone(expired_sub.ends_at, "ALREADY_EXPIRED rows are now auto-expired by --apply")
        self.assertLess(expired_sub.ends_at, self.now, "auto-expired row's ends_at should be the computed past date")
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

    def test_excluded_id_is_never_applied_even_when_otherwise_ok(self):
        """
        An excluded row that would otherwise classify OK (future ends_at)
        must still never be written by --apply. Confirms EXCLUDED is
        checked before, and overrides, the normal OK/EXPIRED/AMBIGUOUS logic.
        """
        sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_excluded_ok")

        with patch(
            "jdasubscriptions.management.commands.backfill_subscription_end_dates.EXCLUDED_SUBSCRIPTION_IDS",
            {"CustomerSubscription": {sub.id}},
        ):
            out = StringIO()
            call_command("backfill_subscription_end_dates", "--apply", stdout=out)

        sub.refresh_from_db()
        self.assertIsNone(sub.ends_at, "EXCLUDED rows must never be written, even if otherwise OK")
        self.assertIn("EXCLUDED", out.getvalue())
        self.assertIn("1 EXCLUDED", out.getvalue())

    def test_excluded_id_is_never_applied_even_when_otherwise_already_expired(self):
        """
        This is the actual real-world shape of all 11 excluded production
        rows: starts_at years in the past, which would otherwise classify
        ALREADY_EXPIRED and now (per the auto-expire decision) get written
        by --apply. The exclusion must still win.
        """
        sub = self._sub(starts_at=self.now - timedelta(days=1500), code_suffix="_excluded_expired")

        with patch(
            "jdasubscriptions.management.commands.backfill_subscription_end_dates.EXCLUDED_SUBSCRIPTION_IDS",
            {"CustomerSubscription": {sub.id}},
        ):
            out = StringIO()
            call_command("backfill_subscription_end_dates", "--apply", stdout=out)

        sub.refresh_from_db()
        self.assertIsNone(
            sub.ends_at,
            "EXCLUDED rows must never be auto-expired, even though they'd otherwise classify ALREADY_EXPIRED",
        )
        self.assertIn("EXCLUDED", out.getvalue())

    def test_exclusion_is_scoped_per_model_not_by_raw_id(self):
        """
        CustomerSubscription and InstitutionSubscription have independent
        primary key sequences, so the same numeric id can legitimately refer
        to two different rows. Excluding an id for one model must not
        exclude the other model's row that happens to share that id.
        """
        customer_sub = self._sub(starts_at=self.now - timedelta(days=1), code_suffix="_scope_customer")

        institution_plan = SubscriptionPlan.objects.create(
            code="test_inst_plan_scope",
            name="Test Institution Plan Scope",
            plan_type="institution",
            billing_period="monthly",
            price_fcfa=5000,
            features=[],
            is_active=True,
        )
        # Force the same numeric pk as customer_sub to prove exclusion is
        # keyed by (model, id), not by id alone.
        institution_sub = InstitutionSubscription.objects.create(
            id=customer_sub.id,
            user=self.user,
            plan=institution_plan,
            status="active",
            starts_at=self.now - timedelta(days=1),
            ends_at=None,
        )

        with patch(
            "jdasubscriptions.management.commands.backfill_subscription_end_dates.EXCLUDED_SUBSCRIPTION_IDS",
            {"CustomerSubscription": {customer_sub.id}},
        ):
            call_command("backfill_subscription_end_dates", "--apply", stdout=StringIO())

        customer_sub.refresh_from_db()
        institution_sub.refresh_from_db()

        self.assertIsNone(customer_sub.ends_at, "excluded CustomerSubscription must not be written")
        self.assertIsNotNone(
            institution_sub.ends_at,
            "InstitutionSubscription with the same numeric id, but not excluded, must still be written",
        )

    def test_hardcoded_exclusion_list_matches_2026_08_25_production_audit(self):
        """
        Pins the actual EXCLUDED_SUBSCRIPTION_IDS content against the 11 ids
        identified in the production admin audit (Denis, Liban, Maggie,
        Stephane, Tonny / ABCO, KEMOLCAPITAL, LECOLEDELABOURSE, SGCS,
        SGI_AGI, SGA2E), so an accidental edit to the list is caught here
        rather than silently changing which real customers are protected.
        """
        from jdasubscriptions.management.commands.backfill_subscription_end_dates import (
            EXCLUDED_SUBSCRIPTION_IDS,
        )

        self.assertEqual(EXCLUDED_SUBSCRIPTION_IDS["CustomerSubscription"], {24, 25, 26, 27, 29})
        self.assertEqual(EXCLUDED_SUBSCRIPTION_IDS["InstitutionSubscription"], {3, 5, 6, 7, 8, 9})


class ExpireOverdueSubscriptionsCommandTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.plan = _make_plan("monthly")
        self.institution_plan = SubscriptionPlan.objects.create(
            code="test_plan_inst_expire", name="Test Inst Plan", plan_type="institution",
            billing_period="monthly", price_fcfa=1000, features=[], is_active=True,
        )

    def _sub(self, username, status, ends_at_offset, model=CustomerSubscription, plan=None):
        user = User.objects.create(username=username)
        return model.objects.create(
            user=user, plan=plan or self.plan, status=status,
            starts_at=self.now - timedelta(days=60),
            ends_at=None if ends_at_offset is None else self.now + ends_at_offset,
        )

    def _run(self, *args):
        out = StringIO()
        call_command("expire_overdue_subscriptions", *args, stdout=out)
        return out.getvalue()

    def _make_matrix(self):
        return {
            "not_due": self._sub("not_due", "active", timedelta(days=10)),
            "due_in_a_minute": self._sub("due_soon", "active", timedelta(minutes=1)),
            "just_overdue": self._sub("just_overdue", "active", -timedelta(minutes=1)),
            "long_overdue": self._sub("long_overdue", "active", -timedelta(days=200)),
            "already_expired": self._sub("already_expired", "expired", -timedelta(days=30)),
            "draft_past": self._sub("draft_past", "draft", -timedelta(days=30)),
            "no_ends_at": self._sub("no_ends_at", "active", None),
            "inst_overdue": self._sub("inst_overdue", "active", -timedelta(days=5),
                                      model=InstitutionSubscription, plan=self.institution_plan),
            "inst_not_due": self._sub("inst_not_due", "active", timedelta(days=5),
                                      model=InstitutionSubscription, plan=self.institution_plan),
        }

    def _statuses(self, subs):
        return {k: type(s).objects.get(pk=s.pk).status for k, s in subs.items()}

    def test_dry_run_reports_but_writes_nothing(self):
        subs = self._make_matrix()
        before = self._statuses(subs)
        out = self._run()
        self.assertEqual(self._statuses(subs), before)
        self.assertIn("3 row(s) would be marked expired", out)
        for name in ("just_overdue", "long_overdue", "inst_overdue"):
            self.assertIn(name, out)
        for name in ("not_due", "due_soon", "no_ends_at", "inst_not_due"):
            self.assertNotIn(f" {name} ", out)

    def test_apply_flips_only_overdue_active_rows(self):
        subs = self._make_matrix()
        out = self._run("--apply")
        self.assertIn("marked 3 row(s) expired", out)
        self.assertEqual(self._statuses(subs), {
            "not_due": "active",
            "due_in_a_minute": "active",
            "just_overdue": "expired",
            "long_overdue": "expired",
            "already_expired": "expired",
            "draft_past": "draft",
            "no_ends_at": "active",
            "inst_overdue": "expired",
            "inst_not_due": "active",
        })

    def test_apply_preserves_ends_at(self):
        sub = self._sub("keep_date", "active", -timedelta(days=5))
        self._run("--apply")
        sub_after = CustomerSubscription.objects.get(pk=sub.pk)
        self.assertEqual(sub_after.ends_at, sub.ends_at)

    def test_flipped_rows_match_access_check(self):
        """Every row the command expires is one access already denies; every row it keeps is still granted."""
        subs = self._make_matrix()
        access_before = {k: _get_active_subscription(s.user) is not None for k, s in subs.items()}
        self._run("--apply")
        for key, sub in subs.items():
            flipped = type(sub).objects.get(pk=sub.pk).status != sub.status
            if flipped:
                self.assertFalse(access_before[key], key)
            if sub.status == "active" and not flipped:
                self.assertTrue(access_before[key], key)

    def test_excluded_legacy_ids_never_touched(self):
        from jdasubscriptions.management.commands.backfill_subscription_end_dates import EXCLUDED_SUBSCRIPTION_IDS
        sub = self._sub("legacy", "active", -timedelta(days=30))
        with patch.dict(EXCLUDED_SUBSCRIPTION_IDS, {"CustomerSubscription": {sub.pk}}):
            self._run("--apply")
        self.assertEqual(CustomerSubscription.objects.get(pk=sub.pk).status, "active")

    def test_idempotent_second_run_is_noop(self):
        self._make_matrix()
        self._run("--apply")
        out = self._run("--apply")
        self.assertIn("Nothing to do", out)

    def test_dry_run_flag_overrides_apply(self):
        sub = self._sub("both_flags", "active", -timedelta(days=1))
        self._run("--apply", "--dry-run")
        self.assertEqual(CustomerSubscription.objects.get(pk=sub.pk).status, "active")


class EffectiveStatusTests(TestCase):
    """
    A stored "active" subscription past its ends_at must read as expired
    everywhere it is displayed or counted, with no scheduled job involved.
    """

    # state -> (stored status, ends_at offset from now, expected effective status)
    STATES = {
        "not_due": ("active", timedelta(days=10), "active"),
        "just_overdue": ("active", -timedelta(minutes=1), "expired"),
        "long_overdue": ("active", -timedelta(days=200), "expired"),
        "no_end_date": ("active", None, "active"),
        "already_expired": ("expired", -timedelta(days=30), "expired"),
    }

    def setUp(self):
        self.now = timezone.now()
        self.plan = _make_plan("monthly", "_eff")
        self.institution_plan = SubscriptionPlan.objects.create(
            code="test_plan_inst_eff", name="Test Inst Plan Eff", plan_type="institution",
            billing_period="monthly", price_fcfa=1000, features=[], is_active=True,
        )
        self.admin = User.objects.create_superuser("eff_admin", "eff_admin@example.com", "pw")
        self.subs = {}
        for name, (status, offset, _) in self.STATES.items():
            user = User.objects.create_user(name, f"{name}@example.com", "pw")
            self.subs[name] = CustomerSubscription.objects.create(
                user=user, plan=self.plan, status=status,
                starts_at=self.now - timedelta(days=300),
                ends_at=None if offset is None else self.now + offset,
            )

    def _expected(self, effective):
        return {n for n, (_, _, e) in self.STATES.items() if e == effective}

    def _names(self, page_obj):
        return {s.user.username for s in page_obj.object_list}

    def test_effective_status_property(self):
        for name, (_, _, expected) in self.STATES.items():
            self.assertEqual(self.subs[name].effective_status, expected, name)

    def test_dashboard_badges_filters_and_counts(self):
        self.client.force_login(self.admin)
        url = reverse("jdasubscriptions:sub_dashboard")

        # Default view (no status param) is Active: only in-date subscriptions.
        resp = self.client.get(url)
        self.assertEqual(self._names(resp.context["customer_page_obj"]), self._expected("active"))

        resp = self.client.get(url, {"status": "expired"})
        self.assertEqual(self._names(resp.context["customer_page_obj"]), self._expected("expired"))

        # "All" view: badge per row matches effective status; Expire button only on in-date rows.
        resp = self.client.get(url, {"status": ""})
        html = resp.content.decode()
        self.assertEqual(self._names(resp.context["customer_page_obj"]), set(self.STATES))
        self.assertEqual(html.count('badge badge-success">Active'), len(self._expected("active")))
        self.assertEqual(html.count('badge badge-danger">Expired'), len(self._expected("expired")))
        for name in self.STATES:
            has_expire_btn = f"Mark subscription #{self.subs[name].pk} as expired" in html
            self.assertEqual(has_expire_btn, name in self._expected("active"), name)

        self.assertEqual(resp.context["total_active"], len(self._expected("active")))
        self.assertEqual(resp.context["total_expired"], len(self._expected("expired")))
        self.assertEqual(resp.context["plan_breakdown"], {self.plan.name: len(self._expected("active"))})

    def test_csv_export_status_and_filter(self):
        self.client.force_login(self.admin)
        url = reverse("jdasubscriptions:export_subscriptions_csv")
        rows = list(csv.reader(StringIO(self.client.get(url).content.decode())))[1:]
        by_user = {r[3]: r[8] for r in rows}
        for name, (_, _, expected) in self.STATES.items():
            self.assertEqual(by_user[name], expected, name)

        rows = list(csv.reader(StringIO(self.client.get(url, {"status": "active"}).content.decode())))[1:]
        self.assertEqual({r[3] for r in rows}, self._expected("active"))

    def test_kpi_dashboard_counts(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("jdasubscriptions:subscription_dashboard"))
        self.assertEqual(resp.context["active_count"], len(self._expected("active")))
        self.assertEqual(resp.context["expired_count"], len(self._expected("expired")))

    @patch("jdasubscriptions.views.initialize_institution_payment")
    def test_plan_switch_only_blocked_for_in_date_subscriptions(self, mock_init):
        from django.http import HttpResponse
        mock_init.return_value = HttpResponse("PAYMENT_INIT")
        url = reverse("jdasubscriptions:select_subscription_plan", args=[self.institution_plan.id])
        for name in self.STATES:
            self.client.force_login(self.subs[name].user)
            resp = self.client.get(url)
            reached_payment = resp.status_code == 200 and resp.content == b"PAYMENT_INIT"
            self.assertEqual(reached_payment, name in self._expected("expired"), name)

    def test_admin_add_only_blocked_for_in_date_subscriptions(self):
        self.client.force_login(self.admin)
        url = reverse("jdasubscriptions:subscription_add")
        for name in self.STATES:
            user = self.subs[name].user
            before = CustomerSubscription.objects.filter(user=user).count()
            self.client.post(url, {
                "subscription_type": "customer", "user": user.pk, "plan": self.plan.pk,
                "start_date": self.now.date().isoformat(), "status": "active",
            })
            created = CustomerSubscription.objects.filter(user=user).count() > before
            self.assertEqual(created, name in self._expected("expired"), name)

    def test_access_check_agrees_with_effective_status(self):
        for name, (_, _, expected) in self.STATES.items():
            has_access = _get_active_subscription(self.subs[name].user) is not None
            self.assertEqual(has_access, expected == "active", name)
