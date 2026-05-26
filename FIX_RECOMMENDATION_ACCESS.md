# Fix: Akwaba Gold "Upgrade Required" on Recommendation Publications

## Bug

Akwaba Gold subscribers see "Upgrade Required" when opening a
`Recommendation` publication, despite their plan having
`{"name": "Recommendations", "visible": true}`.

---

## Root Cause

`user_can_access_publication` in
`jdasubscriptions/services/access_services.py:119–124` uses an exact
string match:

```python
feature.get("name") == publication_type
```

`publication_type` comes from `publication.research_type`, which is the
raw DB value from `PublicationModel.TYPE_CHOICES`.

Migration `0012_update_plan_features` introduced display-friendly names
into the plan JSON (e.g. `"Recommendations"`, `"IPO Review"`) that do not
match the `TYPE_CHOICES` values stored on publications (e.g.
`"Recommendation"`, `"IPO Analysis"`).

---

## Full Mismatch Matrix

Cross-referencing `PublicationModel.TYPE_CHOICES` against Akwaba Gold's
current `features` JSON (post-migration 0012):

| `research_type` on publication | Feature `name` in plan JSON        | Match? |
|--------------------------------|------------------------------------|--------|
| `Research Notes`               | `"Research Notes"`                 | ✅     |
| `Economic Notes`               | `"Economic Notes"`                 | ✅     |
| `Recommendation`               | `"Recommendations"`                | ❌     |
| `IPO Analysis`                 | `"IPO Review"`                     | ❌     |
| `Quarterly Results`            | `"Quarterly Results Commentary"`   | ❌     |
| `Half Year Results`            | `"Semi-annual Results Commentary"` | ❌     |
| `Annual Results`               | `"Annual Results Commentary"`      | ❌     |
| `Shareholder Meeting Feedback` | `"General Meetings Commentary"`    | ❌     |
| `Daily Briefing`               | *(no matching feature)*            | ❌     |
| `Sector Reports`               | *(no matching feature)*            | ❌     |
| `Strategic Reports`            | *(no matching feature)*            | ❌     |

`Newsletters` is unaffected — it is matched by `research_category`, not
`research_type`, via the special-case at `access_services.py:114–115`.

`Stock Pitch`, `Analyst Access`, and `Avis sur valeur*` are display-only
features with no corresponding `research_type`; they gate no
publications.

**Only `Research Notes` and `Economic Notes` have ever worked correctly.**

---

## Recommended Fix: Fix B — Mapping dict in `access_services.py`

### Why Fix B over Fix A

**Fix A** (rename feature `name` values in the DB JSON to match
`research_type` exactly) would also work, but requires:
- A new migration running against production
- User-visible label changes on the subscription plans page
  (`"Quarterly Results Commentary"` → `"Quarterly Results"`, etc.)

**Fix B** (add a normalisation mapping in `access_services.py`):
- Pure code change — no migration, no DB touch
- Feature display names shown to subscribers remain unchanged
- Single file to revert if something goes wrong
- Makes the intent explicit and auditable

---

## Implementation

Edit `jdasubscriptions/services/access_services.py`.

Add the mapping constant near the top of the file (after the imports):

```python
# Maps user-facing feature names in plan JSON to the research_type values
# stored on PublicationModel. Only entries that differ need to appear here.
_FEATURE_NAME_TO_RESEARCH_TYPE = {
    "Recommendations":                "Recommendation",
    "IPO Review":                     "IPO Analysis",
    "Quarterly Results Commentary":   "Quarterly Results",
    "Semi-annual Results Commentary": "Half Year Results",
    "Annual Results Commentary":      "Annual Results",
    "General Meetings Commentary":    "Shareholder Meeting Feedback",
}
```

Update the feature-matching loop in `user_can_access_publication`
(currently at lines 119–124):

**Before:**
```python
for feature in plan.features or []:
    if (
            feature.get("name") == publication_type
            and feature.get("visible") is True
    ):
        return True
```

**After:**
```python
for feature in plan.features or []:
    feature_name = feature.get("name", "")
    resolved = _FEATURE_NAME_TO_RESEARCH_TYPE.get(feature_name, feature_name)
    if resolved == publication_type and feature.get("visible") is True:
        return True
```

No other changes needed. `get_upgrade_recommendation` walks the same
`plan.features` list with the same comparison, so apply the same
substitution there too (lines 202–209):

**Before:**
```python
for plan in eligible_plans:
    for feature in plan.features or []:
        if (
                feature.get("name") == publication_type
                and feature.get("visible") is True
        ):
            required_plan = plan
            break
```

**After:**
```python
for plan in eligible_plans:
    for feature in plan.features or []:
        feature_name = feature.get("name", "")
        resolved = _FEATURE_NAME_TO_RESEARCH_TYPE.get(feature_name, feature_name)
        if resolved == publication_type and feature.get("visible") is True:
            required_plan = plan
            break
```

---

## Verification

Run in `python manage.py shell` (requires `DATABASE_URL` set):

```python
from jdasubscriptions.services.access_services import user_can_access_publication
from jdapublicationsapp.models import PublicationModel
from django.contrib.auth.models import User

# Replace with a real Akwaba Gold subscriber username
user = User.objects.get(username="<akwaba_gold_subscriber>")

# Find any Recommendation publication
pub = PublicationModel.objects.filter(research_type="Recommendation").first()

if pub is None:
    print("No Recommendation publications in DB — create one to test")
else:
    result = user_can_access_publication(user, pub)
    assert result is True, f"FAIL: access denied for {user} on {pub}"
    print(f"PASS: {user.username} can access '{pub.subject}' ({pub.research_type})")
```

To confirm the full matrix is resolved, loop over every affected type:

```python
AFFECTED_TYPES = [
    "Recommendation", "IPO Analysis", "Quarterly Results",
    "Half Year Results", "Annual Results", "Shareholder Meeting Feedback",
]

for rtype in AFFECTED_TYPES:
    pub = PublicationModel.objects.filter(research_type=rtype).first()
    if pub is None:
        print(f"SKIP (no publications): {rtype}")
        continue
    result = user_can_access_publication(user, pub)
    status = "PASS" if result else "FAIL"
    print(f"{status}: {rtype}")
```

---

## Notes on `Daily Briefing`, `Sector Reports`, `Strategic Reports`

These three `research_type` values exist in `PublicationModel.TYPE_CHOICES`
but have no corresponding feature entry in any plan's JSON. Any publication
uploaded with these types will fail the access check for all subscribers.

If publications of these types exist (or will be uploaded), add entries to
the relevant plan JSONs via a new migration, e.g.:

```python
{"name": "Daily Briefing", "visible": True}
```

The `_FEATURE_NAME_TO_RESEARCH_TYPE` mapping would only need an entry if the
display name differs from the `research_type` value.
