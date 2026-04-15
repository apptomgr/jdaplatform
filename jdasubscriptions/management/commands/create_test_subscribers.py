"""
Management command: create_test_subscribers

Creates 4 test users covering every row of the access matrix:

  test_no_plan@jda.com     — no subscription
  test_akwaba@jda.com      — active Akwaba (monthly)
  test_akwabaplus@jda.com  — active Akwaba+ (monthly)
  test_gold@jda.com        — active Akwaba Gold (monthly)

Password for all: TestPass123!

Run:
  python manage.py create_test_subscribers
  python manage.py create_test_subscribers --reset   # delete and recreate
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from jdasubscriptions.models import CustomerSubscription, SubscriptionPlan

User = get_user_model()

PASSWORD = "TestPass123!"

TEST_USERS = [
    {
        "email": "test_no_plan@jda.com",
        "plan_code": None,  # no subscription
    },
    {
        "email": "test_akwaba@jda.com",
        "plan_code": "akwaba_monthly",
    },
    {
        "email": "test_akwabaplus@jda.com",
        "plan_code": "akwaba_plus_monthly",
    },
    {
        "email": "test_gold@jda.com",
        "plan_code": "akwaba_gold_monthly",
    },
]


class Command(BaseCommand):
    help = "Create test subscriber users for Phase 1 access control testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing test users and subscriptions before creating",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            emails = [u["email"] for u in TEST_USERS]
            deleted, _ = User.objects.filter(email__in=emails).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing test user(s)."))

        now = timezone.now()
        end_date = now + timedelta(days=365)

        for spec in TEST_USERS:
            email = spec["email"]
            username = email.split("@")[0]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": username},
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  Created user: {email}"))
            else:
                self.stdout.write(f"  User already exists: {email}")

            # Skip subscription for no-plan user
            if spec["plan_code"] is None:
                self.stdout.write(f"    → no subscription (as intended)")
                continue

            # Look up the plan
            try:
                plan = SubscriptionPlan.objects.get(code=spec["plan_code"])
            except SubscriptionPlan.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"    ✗ Plan '{spec['plan_code']}' not found — skipping subscription for {email}"
                    )
                )
                continue

            # Expire any existing active subscriptions for this user
            CustomerSubscription.objects.filter(
                user=user, status="active"
            ).update(status="expired", ends_at=now)

            # Create fresh active subscription
            sub = CustomerSubscription.objects.create(
                user=user,
                plan=plan,
                status="active",
                starts_at=now,
                ends_at=end_date,
            )
            self.stdout.write(
                self.style.SUCCESS(f"    → active subscription: {plan.name} (ends {end_date.date()})")
            )

        self.stdout.write(self.style.SUCCESS("\nDone. All test users ready."))
        self.stdout.write("")
        self.stdout.write("Login credentials (all passwords: TestPass123!)")
        self.stdout.write("  test_no_plan@jda.com    — no subscription")
        self.stdout.write("  test_akwaba@jda.com     — Akwaba")
        self.stdout.write("  test_akwabaplus@jda.com — Akwaba+")
        self.stdout.write("  test_gold@jda.com       — Akwaba Gold")
