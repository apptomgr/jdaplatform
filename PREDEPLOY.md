# PREDEPLOY.md — Jdaplatform: Pre-Deployment Checklist

## IMPORTANT
Run through this checklist EVERY time before git push.
Do NOT proceed to commit or push if any item is ❌.

---

## Step 1 — Read current settings
Read `settings.py` and report the current values of:
- DEBUG
- DEVELOPMENT_MODE
- ALLOWED_HOSTS
- SUBSCRIPTION_REQUIRED

---

## Step 2 — Production flags check
Confirm the following are set correctly:

```python
DEBUG = False              # ❌ NEVER push with DEBUG=True
DEVELOPMENT_MODE = False   # ❌ NEVER push with DEVELOPMENT_MODE=True
ALLOWED_HOSTS = ['platform.jda-ci.com']  # not '*'
SUBSCRIPTION_REQUIRED = False  # confirm intended value before push
```

⚠️ WARNING: Local .env values must ALWAYS be set to
production-safe values before pushing:
- DEBUG=False
- DEVELOPMENT_MODE=False

Reason: If these are True in .env and DO environment
variables are also set, local .env values may override
DO settings and cause 500 errors in production.

The .env file is for local development only — always
reset to production-safe values before every git push.

If any flag is wrong — fix it before proceeding.
Do NOT proceed until all flags are ✅.

---

## Step 3 — Migrations check
Run:
```bash
python manage.py migrate --check
```
- ✅ No unapplied migrations — safe to proceed
- ❌ Unapplied migrations found — run locally first:
```bash
  python manage.py migrate
  python manage.py migrate --check  # confirm clean
```
  Then commit the migrations before pushing.

Also run:
```bash
python manage.py showmigrations | grep '\[ \]'
```
- ✅ No output — all migrations applied
- ❌ Output found — report which apps have unapplied migrations

---

## Step 4 — No localhost URLs
```bash
grep -r "127.0.0.1" --include="*.py" --include="*.html" --include="*.js" .
grep -r "localhost" --include="*.py" --include="*.html" --include="*.js" .
```
- ✅ No results — safe to proceed
- ❌ Found — report exact file and line, fix before proceeding

---

## Step 5 — No debug artifacts
```bash
grep -r "print(" --include="*.py" .
grep -r "console.log" --include="*.html" --include="*.js" .
grep -r "debugger" --include="*.html" --include="*.js" .
```
- ✅ No results — safe to proceed
- ❌ Found — report and remove before proceeding

---

## Step 6 — Requirements up to date
```bash
pip freeze > requirements_check.txt
diff requirements.txt requirements_check.txt
rm requirements_check.txt
```
- ✅ No diff output — requirements.txt is current
- ❌ Diff found — update requirements.txt:
```bash
  pip freeze > requirements.txt
```

---

## Step 7 — Local smoke test
Start server and verify these URLs respond correctly:
```bash
python manage.py runserver
```

Check:
- http://127.0.0.1:8000/ → ✅ loads without 500 error
- http://127.0.0.1:8000/jdapublicationsapp/jdapublicationsapp_pubs/ → ✅ loads
- http://127.0.0.1:8000/jdasubscriptions/api/public/subscription-plans/ → ✅ returns JSON
- http://127.0.0.1:8000/jdasubscriptions/sub_dashboard/ → ✅ loads for staff user

---

## Step 8 — Git status review
```bash
git status
git diff --name-only
```
Report all modified files.
Confirm ONLY intended files are staged — no accidental changes.

---

## Step 9 — Checklist sign-off
Report ✅ or ❌ for every step before proceeding.
