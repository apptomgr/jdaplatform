from django.db import migrations


AKWABA_FEATURES = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendations", "visible": True, "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": False},
    {"name": "Analyst Access", "visible": False},
    {"name": "Research Notes", "visible": False},
    {"name": "Economic Notes", "visible": False},
    {"name": "Avis sur valeur*", "visible": False},
]

AKWABA_PLUS_FEATURES = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendations", "visible": True, "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": True},
    {"name": "Analyst Access", "visible": False},
    {"name": "Research Notes", "visible": False},
    {"name": "Economic Notes", "visible": False},
    {"name": "Avis sur valeur*", "visible": False},
]

AKWABA_GOLD_FEATURES = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendations", "visible": True, "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": True},
    {"name": "Analyst Access", "visible": True},
    {"name": "Research Notes", "visible": True},
    {"name": "Economic Notes", "visible": True},
    {"name": "Avis sur valeur*", "visible": True},
]

# Reverse: restore the original flat structure (no sub_items)
AKWABA_FEATURES_ORIG = [
    {"name": "Newsletters", "visible": True},
    {"name": "IPO Review", "visible": True},
    {"name": "Recommendation", "visible": True},
    {"name": "Top 10 Buy", "visible": True},
    {"name": "Top 10 Sell", "visible": True},
    {"name": "Quarterly Results Commentary", "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary", "visible": True},
    {"name": "General Meetings Commentary", "visible": True},
    {"name": "Stock Pitch", "visible": False},
    {"name": "Analyst Access", "visible": False},
    {"name": "Research Notes", "visible": False},
    {"name": "Economic Notes", "visible": False},
]

AKWABA_PLUS_FEATURES_ORIG = [
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
    {"name": "Research Notes", "visible": False},
    {"name": "Economic Notes", "visible": False},
]

AKWABA_GOLD_FEATURES_ORIG = [
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
    SubscriptionPlan.objects.filter(name="Akwaba").update(features=AKWABA_FEATURES)
    SubscriptionPlan.objects.filter(name="Akwaba+").update(features=AKWABA_PLUS_FEATURES)
    SubscriptionPlan.objects.filter(name="Akwaba Gold").update(features=AKWABA_GOLD_FEATURES)


def reverse_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(name="Akwaba").update(features=AKWABA_FEATURES_ORIG)
    SubscriptionPlan.objects.filter(name="Akwaba+").update(features=AKWABA_PLUS_FEATURES_ORIG)
    SubscriptionPlan.objects.filter(name="Akwaba Gold").update(features=AKWABA_GOLD_FEATURES_ORIG)


class Migration(migrations.Migration):

    dependencies = [
        ("jdasubscriptions", "0011_alter_customersubscription_paystack_reference_and_more"),
    ]

    operations = [
        migrations.RunPython(update_features, reverse_code=reverse_features),
    ]
