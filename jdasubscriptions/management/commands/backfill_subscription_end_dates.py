"""
Management command: backfill_subscription_end_dates

Every subscription activated through the (previously broken) Paystack
callback flow was left with `ends_at=NULL`, which the active-subscription
query treats as "never expires". This backfills `ends_at` for currently
active subscriptions that are missing it, computed as
`starts_at + BILLING_PERIOD_DELTA[plan.billing_period]`.

Classification per row:
  OK              — ends_at can be computed unambiguously and is in the
                    future (or now). Written on --apply.
  ALREADY_EXPIRED — the computed ends_at is already in the past. NEVER
                    written by --apply, regardless of flags. Cutting off
                    a customer who's had access this whole time needs a
                    prior notification, which is a manual follow-up
                    outside this command.
  AMBIGUOUS       — starts_at is missing, or plan.billing_period isn't in
                    the known table. Never written; needs manual review.

Run:
  python manage.py backfill_subscription_end_dates            # dry run (default)
  python manage.py backfill_subscription_end_dates --dry-run  # same, explicit
  python manage.py backfill_subscription_end_dates --apply    # writes OK rows only
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from jdasubscriptions.billing import BILLING_PERIOD_DELTA
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription


class Command(BaseCommand):
    help = "Backfill ends_at for active subscriptions where it was never set."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write ends_at for OK rows. Without this flag, only reports what would change.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        now = timezone.now()

        rows = []
        for model in (CustomerSubscription, InstitutionSubscription):
            qs = model.objects.filter(
                status="active", ends_at__isnull=True
            ).select_related("plan", "user")
            for sub in qs:
                rows.append(self._classify(model, sub, now))

        if not rows:
            self.stdout.write(self.style.SUCCESS("No active subscriptions with ends_at=NULL. Nothing to do."))
            return

        self._print_report(rows)

        ok_rows = [r for r in rows if r["classification"] == "OK"]
        expired_rows = [r for r in rows if r["classification"] == "ALREADY_EXPIRED"]
        ambiguous_rows = [r for r in rows if r["classification"] == "AMBIGUOUS"]

        self.stdout.write("")
        self.stdout.write(
            f"Summary: {len(ok_rows)} OK, {len(expired_rows)} ALREADY_EXPIRED "
            f"(never auto-applied), {len(ambiguous_rows)} AMBIGUOUS (needs manual review)."
        )

        if not apply_changes:
            self.stdout.write(self.style.WARNING("\nDry run only — no rows were written. Re-run with --apply to write OK rows."))
            return

        for row in ok_rows:
            row["subscription"].ends_at = row["computed_ends_at"]
            row["subscription"].save(update_fields=["ends_at"])

        self.stdout.write(self.style.SUCCESS(f"\nApplied: wrote ends_at for {len(ok_rows)} row(s)."))
        if expired_rows:
            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {len(expired_rows)} ALREADY_EXPIRED row(s) — these need customer "
                    "notification before anyone sets ends_at on them."
                )
            )
        if ambiguous_rows:
            self.stdout.write(
                self.style.WARNING(f"Skipped {len(ambiguous_rows)} AMBIGUOUS row(s) — needs manual review.")
            )

    def _classify(self, model, sub, now):
        plan = sub.plan
        billing_period = getattr(plan, "billing_period", None)

        if not sub.starts_at:
            return {
                "model": model.__name__,
                "subscription": sub,
                "classification": "AMBIGUOUS",
                "reason": "starts_at is not set",
                "computed_ends_at": None,
            }

        delta = BILLING_PERIOD_DELTA.get(billing_period)
        if delta is None:
            return {
                "model": model.__name__,
                "subscription": sub,
                "classification": "AMBIGUOUS",
                "reason": f"unrecognized billing_period {billing_period!r} on plan {plan.code!r}",
                "computed_ends_at": None,
            }

        computed_ends_at = sub.starts_at + delta

        if computed_ends_at < now:
            return {
                "model": model.__name__,
                "subscription": sub,
                "classification": "ALREADY_EXPIRED",
                "reason": None,
                "computed_ends_at": computed_ends_at,
            }

        return {
            "model": model.__name__,
            "subscription": sub,
            "classification": "OK",
            "reason": None,
            "computed_ends_at": computed_ends_at,
        }

    def _print_report(self, rows):
        header = f"{'ID':>5}  {'Type':<12}  {'User':<28}  {'Plan':<28}  {'starts_at':<20}  {'computed ends_at':<20}  {'STATUS'}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for row in rows:
            sub = row["subscription"]
            user_label = getattr(sub.user, "email", None) or getattr(sub.user, "username", str(sub.user_id))
            plan_label = f"{sub.plan.name} ({sub.plan.billing_period})"
            starts_at_label = sub.starts_at.strftime("%Y-%m-%d %H:%M") if sub.starts_at else "—"
            ends_at_label = row["computed_ends_at"].strftime("%Y-%m-%d %H:%M") if row["computed_ends_at"] else "—"

            status = row["classification"]
            if row["reason"]:
                status = f"{status} ({row['reason']})"

            style = self.style.SUCCESS if row["classification"] == "OK" else self.style.WARNING
            self.stdout.write(style(
                f"{sub.id:>5}  {row['model']:<12}  {user_label:<28}  {plan_label:<28}  "
                f"{starts_at_label:<20}  {ends_at_label:<20}  {status}"
            ))
