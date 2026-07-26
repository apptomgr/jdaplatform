from django.db import migrations


def normalize_gold_access_quarterly_name(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    SubscriptionPlan.objects.filter(
        name='Gold Access Quarterly',
        plan_type='institution',
    ).update(name='Gold Access', billing_period='quarterly')


def reverse_normalize_gold_access_quarterly_name(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    SubscriptionPlan.objects.filter(
        name='Gold Access',
        plan_type='institution',
        billing_period='quarterly',
    ).update(name='Gold Access Quarterly')


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0019_fix_silver_access_features'),
    ]

    operations = [
        migrations.RunPython(
            normalize_gold_access_quarterly_name,
            reverse_code=reverse_normalize_gold_access_quarterly_name,
        ),
    ]
