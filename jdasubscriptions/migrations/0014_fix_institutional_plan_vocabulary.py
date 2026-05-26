from django.db import migrations


GOLD_ACCESS_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                    "visible": True},
    {"name": "IPO Review",                     "visible": True},
    {"name": "Recommendations",                "visible": True},
    {"name": "Research Notes",                 "visible": True},
    {"name": "Economic Notes",                 "visible": True},
    {"name": "Quarterly Results Commentary",   "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary",      "visible": True},
    {"name": "General Meetings Commentary",    "visible": True},
    {"name": "Avis sur valeur*",               "visible": True},
    {"name": "Analyst Access",                 "visible": True},
    {"name": "Corporate Access",               "visible": True},
]

SILVER_ACCESS_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                    "visible": True},
    {"name": "IPO Review",                     "visible": True},
    {"name": "Recommendations",                "visible": True},
    {"name": "Research Notes",                 "visible": True},
    {"name": "Economic Notes",                 "visible": True},
    {"name": "Quarterly Results Commentary",   "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary",      "visible": True},
    {"name": "General Meetings Commentary",    "visible": True},
    {"name": "Avis sur valeur*",               "visible": True},
    {"name": "Analyst Access",                 "visible": False},
    {"name": "Corporate Access",               "visible": False},
]

# Reverse: restore the 0013 feature lists
GOLD_ACCESS_FEATURES_ORIG = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                    "visible": True},
    {"name": "Research Notes",                 "visible": True},
    {"name": "IPO Reviews",                    "visible": True},
    {"name": "Economic Notes",                 "visible": True},
    {"name": "Quarterly Results Commentary",   "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary",      "visible": True},
    {"name": "General Meetings Commentary",    "visible": True},
    {"name": "Avis sur valeur*",               "visible": True},
    {"name": "Analyst Access",                 "visible": True},
    {"name": "Corporate Access",               "visible": True},
]

SILVER_ACCESS_FEATURES_ORIG = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                    "visible": True},
    {"name": "Research Notes",                 "visible": True},
    {"name": "IPO Reviews",                    "visible": True},
    {"name": "Economic Notes",                 "visible": True},
    {"name": "Quarterly Results Commentary",   "visible": True},
    {"name": "Semi-annual Results Commentary", "visible": True},
    {"name": "Annual Results Commentary",      "visible": True},
    {"name": "General Meetings Commentary",    "visible": True},
    {"name": "Avis sur valeur*",               "visible": True},
    {"name": "Analyst Access",                 "visible": False},
    {"name": "Corporate Access",               "visible": False},
]


def update_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(
        name__in=["Gold Access", "Gold Access Quarterly"],
        plan_type="institution",
    ).update(features=GOLD_ACCESS_FEATURES)
    SubscriptionPlan.objects.filter(
        name="Silver Access",
        plan_type="institution",
    ).update(features=SILVER_ACCESS_FEATURES)


def reverse_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(
        name__in=["Gold Access", "Gold Access Quarterly"],
        plan_type="institution",
    ).update(features=GOLD_ACCESS_FEATURES_ORIG)
    SubscriptionPlan.objects.filter(
        name="Silver Access",
        plan_type="institution",
    ).update(features=SILVER_ACCESS_FEATURES_ORIG)


class Migration(migrations.Migration):

    dependencies = [
        ("jdasubscriptions", "0013_update_institutional_plan_features"),
    ]

    operations = [
        migrations.RunPython(update_features, reverse_code=reverse_features),
    ]
