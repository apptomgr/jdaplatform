import copy
from django.db import migrations

SILVER_EXCEPTIONS = {'Opinion on all stocks', 'Analyst Access'}


def fix_silver_access_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    gold_template = SubscriptionPlan.objects.get(name='Gold Access', billing_period='monthly')

    for silver in SubscriptionPlan.objects.filter(name='Silver Access'):
        new_features = []
        for feature in copy.deepcopy(gold_template.features):
            if feature['name'] in SILVER_EXCEPTIONS:
                feature['visible'] = False
            new_features.append(feature)
        silver.features = new_features
        silver.save()


def reverse_fix_silver_access_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    # Snapshot of Silver Access monthly features before the migration (from migration 0018 state)
    original_features = [
        {'name': 'Access to all publications available on the platform', 'visible': True},
        {'name': 'Newsletters', 'visible': True},
        {'name': 'IPO Analysis', 'visible': True},
        {'name': 'Recommendations', 'visible': True, 'sub_items': ['Stock Opinion']},
        {'name': 'Research Notes', 'visible': True},
        {'name': 'Economic Notes', 'visible': True},
        {'name': 'Opinion on all stocks', 'visible': False},
        {'name': 'Quarterly Results Commentary', 'visible': True},
        {'name': 'Semi-annual Results', 'visible': True},
        {'name': 'Annual Results', 'visible': True},
        {'name': 'General Meetings Commentary', 'visible': True},
        {'name': 'Analyst Access', 'visible': False},
    ]

    for silver in SubscriptionPlan.objects.filter(name='Silver Access'):
        silver.features = copy.deepcopy(original_features)
        silver.save()


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0018_fix_plan_features'),
    ]

    operations = [
        migrations.RunPython(
            fix_silver_access_features,
            reverse_code=reverse_fix_silver_access_features,
        ),
    ]
