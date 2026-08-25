from dateutil.relativedelta import relativedelta

# Duration added to `starts_at` to compute `ends_at` for a subscription.
# Keys must cover every SubscriptionPlan.billing_period value.
BILLING_PERIOD_DELTA = {
    "monthly": relativedelta(months=1),
    "quarterly": relativedelta(months=3),
    "yearly": relativedelta(years=1),
}
