from django.db import migrations

RENAME_MAP = {
    'Semi-annual Results': 'Half Year Results Commentary',
    'Annual Results': 'Annual Results Commentary',
}

REVERSE_RENAME_MAP = {v: k for k, v in RENAME_MAP.items()}


def _rename_features(apps, name_map):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')
    for plan in SubscriptionPlan.objects.all():
        features = plan.features
        if not isinstance(features, list):
            continue
        changed = False
        for feature in features:
            if isinstance(feature, dict) and feature.get('name') in name_map:
                feature['name'] = name_map[feature['name']]
                changed = True
        if changed:
            plan.save(update_fields=['features'])


def rename_forward(apps, schema_editor):
    _rename_features(apps, RENAME_MAP)


def rename_reverse(apps, schema_editor):
    _rename_features(apps, REVERSE_RENAME_MAP)


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0020_normalize_gold_access_quarterly_name'),
    ]

    operations = [
        migrations.RunPython(
            rename_forward,
            reverse_code=rename_reverse,
        ),
    ]
