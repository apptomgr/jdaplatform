"""
Management command: expire_overdue_subscriptions

Flips `status` from "active" to "expired" on subscriptions whose `ends_at`
has passed. Access itself is already enforced at request time by
`_get_active_subscription()` (which requires `ends_at >= now`), so this
command does not change who can read publications — it keeps the stored
status in line with reality, so the Subscription Dashboard, its stats, and
the status-only checks elsewhere (cross-model plan switching, manual
subscription creation) stop treating lapsed subscribers as active.

Selection is the exact negation of `_get_active_subscription()`'s ends_at
clause: status="active" AND ends_at < now. Rows with ends_at=NULL are never
touched (that's how pre-Paystack legacy customers are stored), and rows in
backfill_subscription_end_dates.EXCLUDED_SUBSCRIPTION_IDS are skipped as a
second safeguard. `ends_at` is left as-is so the real lapse date is kept.

Intended to run daily as a scheduled job with --apply.

Run:
  python manage.py expire_overdue_subscriptions            # dry run (default)
  python manage.py expire_overdue_subscriptions --dry-run  # same, explicit
  python manage.py expire_overdue_subscriptions --apply    # writes status="expired"
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from jdasubscriptions.management.commands.backfill_subscription_end_dates import EXCLUDED_SUBSCRIPTION_IDS
from jdasubscriptions.models import CustomerSubscription, InstitutionSubscription


def overdue_subscriptions(model, now):
    """Active rows that _get_active_subscription() already rejects on ends_at."""
    excluded_ids = EXCLUDED_SUBSCRIPTION_IDS.get(model.__name__, set())
    return (
        model.objects
        .filter(status="active", ends_at__isnull=False, ends_at__lt=now)
        .exclude(pk__in=excluded_ids)
    )


class Command(BaseCommand):
    help = "Mark active subscriptions whose ends_at has passed as expired."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write status='expired' for overdue rows. Without this flag, only reports what would change.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Explicit no-op — dry-run is already the default whenever --apply is omitted.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"] and not options["dry_run"]
        now = timezone.now()

        rows = []
        for model in (CustomerSubscription, InstitutionSubscription):
            for sub in overdue_subscriptions(model, now).select_related("plan", "user").order_by("ends_at"):
                rows.append((model, sub))

        self.stdout.write(f"Run at {now:%Y-%m-%d %H:%M %Z}")

        if not rows:
            self.stdout.write(self.style.SUCCESS("No overdue active subscriptions. Nothing to do."))
            return

        self._print_report(rows, now)

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                f"\nDry run only — {len(rows)} row(s) would be marked expired. "
                "Re-run with --apply to write."
            ))
            return

        # Re-apply the same filter in the UPDATE so a row renewed/extended
        # between the read above and this write is not expired.
        updated = 0
        for model in (CustomerSubscription, InstitutionSubscription):
            ids = [sub.pk for m, sub in rows if m is model]
            if ids:
                updated += overdue_subscriptions(model, now).filter(pk__in=ids).update(status="expired")

        self.stdout.write(self.style.SUCCESS(f"\nApplied: marked {updated} row(s) expired."))

    def _print_report(self, rows, now):
        header = f"{'ID':>5}  {'Type':<24}  {'User':<28}  {'Plan':<28}  {'ends_at':<16}  {'Overdue'}"
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for model, sub in rows:
            user_label = getattr(sub.user, "email", None) or getattr(sub.user, "username", str(sub.user_id))
            plan_label = f"{sub.plan.name} ({sub.plan.billing_period})"
            self.stdout.write(
                f"{sub.id:>5}  {model.__name__:<24}  {user_label:<28}  {plan_label:<28}  "
                f"{sub.ends_at:%Y-%m-%d %H:%M}  {(now - sub.ends_at).days}d"
            )
