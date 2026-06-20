import copy
from django.db import migrations


def fix_plan_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    for plan in SubscriptionPlan.objects.all():
        features = copy.deepcopy(plan.features)
        new_features = []
        analyst_access = None

        for feature in features:
            name = feature.get('name')

            # Fix A: rename "Avis sur valeur" → "Stock Opinion" in sub_items / sub_items_excluded
            if name == 'Recommendations':
                if 'sub_items' in feature:
                    feature['sub_items'] = [
                        'Stock Opinion' if s == 'Avis sur valeur' else s
                        for s in feature['sub_items']
                    ]
                if 'sub_items_excluded' in feature:
                    feature['sub_items_excluded'] = [
                        'Stock Opinion' if s == 'Avis sur valeur' else s
                        for s in feature['sub_items_excluded']
                    ]

            # Fix B: drop the duplicate "Avis sur toutes les valeurs" feature
            if name == 'Avis sur toutes les valeurs':
                continue

            # Fix C: hold "Analyst Access" aside so we can append it last
            if name == 'Analyst Access':
                analyst_access = feature
                continue

            new_features.append(feature)

        # Fix C: re-append Analyst Access at the end
        if analyst_access is not None:
            new_features.append(analyst_access)

        plan.features = new_features
        plan.save()


def reverse_fix_plan_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    for plan in SubscriptionPlan.objects.all():
        features = copy.deepcopy(plan.features)
        new_features = []
        analyst_access = None

        for feature in features:
            name = feature.get('name')

            # Reverse A: rename "Stock Opinion" → "Avis sur valeur"
            if name == 'Recommendations':
                if 'sub_items' in feature:
                    feature['sub_items'] = [
                        'Avis sur valeur' if s == 'Stock Opinion' else s
                        for s in feature['sub_items']
                    ]
                if 'sub_items_excluded' in feature:
                    feature['sub_items_excluded'] = [
                        'Avis sur valeur' if s == 'Stock Opinion' else s
                        for s in feature['sub_items_excluded']
                    ]

            # Reverse C: pull Analyst Access out again
            if name == 'Analyst Access':
                analyst_access = feature
                continue

            new_features.append(feature)

            # Reverse B: re-insert "Avis sur toutes les valeurs" after "Opinion on all stocks"
            if name == 'Opinion on all stocks':
                new_features.append({
                    'name': 'Avis sur toutes les valeurs',
                    'visible': feature.get('visible', False),
                })

        # Reverse C: restore Analyst Access just before "Research Notes"
        if analyst_access is not None:
            try:
                idx = next(
                    i for i, f in enumerate(new_features)
                    if f.get('name') == 'Research Notes'
                )
                new_features.insert(idx, analyst_access)
            except StopIteration:
                new_features.append(analyst_access)

        plan.features = new_features
        plan.save()


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0017_add_quarterly_customer_plans'),
    ]

    operations = [
        migrations.RunPython(fix_plan_features, reverse_code=reverse_fix_plan_features),
    ]
