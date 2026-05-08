from django.db import migrations


SILVER_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters", "visible": True},
    {"name": "Research Notes", "visible": True},
    {"name": "IPO Reviews", "visible": True},
    {"name": "Economic Notes", "visible": True},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Avis sur valeur*", "visible": True},
    {"name": "Analyst Access", "visible": False},
    {"name": "Corporate Access", "visible": False},
]

GOLD_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters", "visible": True},
    {"name": "Research Notes", "visible": True},
    {"name": "IPO Reviews", "visible": True},
    {"name": "Economic Notes", "visible": True},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Avis sur valeur*", "visible": True},
    {"name": "Analyst Access", "visible": True},
    {"name": "Corporate Access", "visible": True},
]

# Reverse: restore the previous flat structure (no sub_items, old feature set)
SILVER_FEATURES_ORIG = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendation", "visible": True},
    {"name": "Top 10 Buy", "visible": True},
    {"name": "Top 10 Sell", "visible": True},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": True},
    {"name": "Analyst Access", "visible": True},
    {"name": "Research Notes", "visible": True},
    {"name": "Economic Notes", "visible": True},
]

GOLD_FEATURES_ORIG = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendation", "visible": True},
    {"name": "Top 10 Buy", "visible": True},
    {"name": "Top 10 Sell", "visible": True},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": True},
    {"name": "Analyst Access", "visible": True},
    {"name": "Research Notes", "visible": True},
    {"name": "Economic Notes", "visible": True},
]


def update_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(name="Silver Access").update(features=SILVER_FEATURES)
    SubscriptionPlan.objects.filter(name__startswith="Gold Access").update(features=GOLD_FEATURES)


def reverse_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(name="Silver Access").update(features=SILVER_FEATURES_ORIG)
    SubscriptionPlan.objects.filter(name__startswith="Gold Access").update(features=GOLD_FEATURES_ORIG)


class Migration(migrations.Migration):

    dependencies = [
        ("jdasubscriptions", "0012_update_plan_features"),
    ]

    operations = [
        migrations.RunPython(update_features, reverse_code=reverse_features),
    ]
