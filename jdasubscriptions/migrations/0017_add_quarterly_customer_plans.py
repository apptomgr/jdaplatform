from django.db import migrations


def add_quarterly_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')

    for name, price in [('Akwaba', 7000), ('Akwaba+', 14000), ('Akwaba Gold', 70000)]:
        monthly = SubscriptionPlan.objects.get(name=name, billing_period='monthly')
        quarterly_code = monthly.code.replace('monthly', 'quarterly')
        SubscriptionPlan.objects.create(
            name=monthly.name,
            code=quarterly_code,
            billing_period='quarterly',
            price_fcfa=price,
            plan_type=monthly.plan_type,
            display_order=monthly.display_order,
            description=monthly.description,
            features=monthly.features,
            is_active=True,
        )


def remove_quarterly_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('jdasubscriptions', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(
        name__in=['Akwaba', 'Akwaba+', 'Akwaba Gold'],
        billing_period='quarterly',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('jdasubscriptions', '0016_change1_plan_feature_updates'),
    ]

    operations = [
        migrations.RunPython(add_quarterly_plans, reverse_code=remove_quarterly_plans),
    ]
