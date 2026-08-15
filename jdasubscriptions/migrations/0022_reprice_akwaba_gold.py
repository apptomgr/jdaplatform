from django.db import migrations

OLD_PRICES = {
    "monthly": 25000,
    "quarterly": 70000,
    "yearly": 250000,
}

NEW_PRICES = {
    "monthly": 50000,
    "quarterly": 140000,
    "yearly": 500000,
}


def reprice_akwaba_gold(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    for billing_period, price in NEW_PRICES.items():
        SubscriptionPlan.objects.filter(
            name='Akwaba Gold',
            billing_period=billing_period,
        ).update(price_fcfa=price)


def reverse_reprice_akwaba_gold(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    for billing_period, price in OLD_PRICES.items():
        SubscriptionPlan.objects.filter(
            name='Akwaba Gold',
            billing_period=billing_period,
        ).update(price_fcfa=price)


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0021_rename_semiannual_annual_results_features'),
    ]

    operations = [
        migrations.RunPython(
            reprice_akwaba_gold,
            reverse_code=reverse_reprice_akwaba_gold,
        ),
    ]
