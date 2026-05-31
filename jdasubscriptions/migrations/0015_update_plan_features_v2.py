from django.db import migrations

# ───────────────────────── NEW feature lists ─────────────────────────

AKWABA_FEATURES = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Analysis",                  "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell", "Stock Opinion"],
     "sub_items_excluded": ["Stock Opinion"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results",           "visible": True},
    {"name": "Annual Results",                "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": False},
    {"name": "Analyst Access",                "visible": False},
    {"name": "Research Notes",                "visible": False},
    {"name": "Economic Notes",                "visible": False},
    {"name": "Opinion on all stocks",         "visible": False},
    {"name": "Avis sur valeur*",              "visible": False},
]

AKWABA_PLUS_FEATURES = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Analysis",                  "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell", "Stock Opinion"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results",           "visible": True},
    {"name": "Annual Results",                "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": True},
    {"name": "Analyst Access",                "visible": False},
    {"name": "Research Notes",                "visible": False},
    {"name": "Economic Notes",                "visible": False},
    {"name": "Opinion on all stocks",         "visible": False},
    {"name": "Avis sur valeur*",              "visible": False},
]

AKWABA_GOLD_FEATURES = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Analysis",                  "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell", "Stock Opinion"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results",           "visible": True},
    {"name": "Annual Results",                "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": True},
    {"name": "Analyst Access",                "visible": True},
    {"name": "Research Notes",                "visible": True},
    {"name": "Economic Notes",                "visible": True},
    {"name": "Opinion on all stocks",         "visible": True},
    {"name": "Avis sur valeur*",              "visible": True},
]

GOLD_ACCESS_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Analysis",                  "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Stock Opinion"]},
    {"name": "Research Notes",                "visible": True},
    {"name": "Economic Notes",                "visible": True},
    {"name": "Opinion on all stocks",         "visible": True},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results",           "visible": True},
    {"name": "Annual Results",                "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Avis sur valeur*",              "visible": True},
    {"name": "Analyst Access",                "visible": True},
    {"name": "Corporate Access",              "visible": True},
]

SILVER_ACCESS_FEATURES = [
    {"name": "Access to all publications available on the platform", "visible": True},
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Analysis",                  "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Stock Opinion"]},
    {"name": "Research Notes",                "visible": True},
    {"name": "Economic Notes",                "visible": True},
    {"name": "Opinion on all stocks",         "visible": False},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results",           "visible": True},
    {"name": "Annual Results",                "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Avis sur valeur*",              "visible": True},
    {"name": "Analyst Access",                "visible": False},
    {"name": "Corporate Access",              "visible": False},
]


# ───────────────────────── PREVIOUS feature lists (for reverse) ─────────────────────────

AKWABA_FEATURES_PREV = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Review",                    "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results Commentary","visible": True},
    {"name": "Annual Results Commentary",     "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": False},
    {"name": "Analyst Access",                "visible": False},
    {"name": "Research Notes",                "visible": False},
    {"name": "Economic Notes",                "visible": False},
    {"name": "Avis sur valeur*",              "visible": False},
]

AKWABA_PLUS_FEATURES_PREV = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Review",                    "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results Commentary","visible": True},
    {"name": "Annual Results Commentary",     "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": True},
    {"name": "Analyst Access",                "visible": False},
    {"name": "Research Notes",                "visible": False},
    {"name": "Economic Notes",                "visible": False},
    {"name": "Avis sur valeur*",              "visible": False},
]

AKWABA_GOLD_FEATURES_PREV = [
    {"name": "Newsletters",                   "visible": True},
    {"name": "IPO Review",                    "visible": True},
    {"name": "Recommendations",               "visible": True,
     "sub_items": ["Top 10 Buy", "Top 10 Sell"]},
    {"name": "Quarterly Results Commentary",  "visible": True},
    {"name": "Semi-annual Results Commentary","visible": True},
    {"name": "Annual Results Commentary",     "visible": True},
    {"name": "General Meetings Commentary",   "visible": True},
    {"name": "Stock Pitch",                   "visible": True},
    {"name": "Analyst Access",                "visible": True},
    {"name": "Research Notes",                "visible": True},
    {"name": "Economic Notes",                "visible": True},
    {"name": "Avis sur valeur*",              "visible": True},
]

GOLD_ACCESS_FEATURES_PREV = [
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

SILVER_ACCESS_FEATURES_PREV = [
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


def update_features(apps, schema_editor):
    SubscriptionPlan = apps.get_model("jdasubscriptions", "SubscriptionPlan")
    SubscriptionPlan.objects.filter(name="Akwaba").update(features=AKWABA_FEATURES)
    SubscriptionPlan.objects.filter(name="Akwaba+").update(features=AKWABA_PLUS_FEATURES)
    SubscriptionPlan.objects.filter(name="Akwaba Gold").update(features=AKWABA_GOLD_FEATURES)
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
    SubscriptionPlan.objects.filter(name="Akwaba").update(features=AKWABA_FEATURES_PREV)
    SubscriptionPlan.objects.filter(name="Akwaba+").update(features=AKWABA_PLUS_FEATURES_PREV)
    SubscriptionPlan.objects.filter(name="Akwaba Gold").update(features=AKWABA_GOLD_FEATURES_PREV)
    SubscriptionPlan.objects.filter(
        name__in=["Gold Access", "Gold Access Quarterly"],
        plan_type="institution",
    ).update(features=GOLD_ACCESS_FEATURES_PREV)
    SubscriptionPlan.objects.filter(
        name="Silver Access",
        plan_type="institution",
    ).update(features=SILVER_ACCESS_FEATURES_PREV)


class Migration(migrations.Migration):

    dependencies = [
        ("jdasubscriptions", "0014_fix_institutional_plan_vocabulary"),
    ]

    operations = [
        migrations.RunPython(update_features, reverse_code=reverse_features),
    ]
