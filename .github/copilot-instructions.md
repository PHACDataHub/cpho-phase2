# What's in this repo

This app is the management/versioning system for public health metrics of Canada. App users are internal government employees. Nearly everything lives in the server/ dir.

Indicators are the backbone model that data gets attached to: user permissions, data linked to periods, benchmarking data for OECD countries, trend data.

# App dev notes

code style

- classes
  - django.utils.functional.cached_property decorator encouraged, especially for form/formset/model instantiation
  - Split complex methods using the single-resp principle
- prefer conditional blocks to ternary expr
- prefer comprehensions to loops (unless nested)
- Dont over-comment obvious code

Commands: Run manage.py commands from the server/ directory (`python manage.py {command}`) to avoid path errors. Run `makemigrations` as needed when touching models

Localization

- All user-facing text should be externalized and rendered via tm(). In jinja, tm is a global, in python, it's `proj.text.tm`
- Every (unique) tm() key should have an entry in the `server/proj/translations.py` dict. If adding new text, add translations at bottom of dict

Jinja

- Use macros for reusability or to avoid nesting
- Inline macros are fine, or add them to macro modules
- Only create additional files (macros, JS) when it gets long, complex, or reused

CSS

- CSS overrides in server/static/cpho.css
- Use bootstrap 5 classes, prefer `.{row}{col}` to .d-flex when equally valid

Models

- Follow patterns in existing models, e.g. versioning decorator, custom fields, verbose_name
- Avoid N+1 queries with select_related and prefetch_related as needed

Views:

- use class-based views, django generic views encouraged
- Some older views are registered in urls.py, new views should import `proj.router.router` and use `@router.route` instead

Forms

- ModelForm and proj.form_util.StandardFormMixin encouraged
- Prefer rendering forms using macros and the generic_form jinja partial
- Manual rendering of fields discouraged unless prompted

Authorization

- Use django-rules (rules.py), with test_rule checks in views.py as needed
- Always import `phac_aspc.rules.test_rule`, dont import from local rules
- Views with perm-logic should use a mixin, usually override dispatch()
- in jinja use global `respects_rule()`

UI/UX

- Prioritize WCAG, unprompted icons discouraged
- Plain HTML/CSS > HTMX > Vanilla JS, NO jquery
  - test suite does not cover htmx or JS interactions, avoid unless necessary
- Modals discouraged, follow existing pattern strictly

# Testing

Write pytests in the server/tests/, focus on integration tests of views, unit tests for helpers

- No need for @mark.django_db, tests already have db access and run in transactions
- Use factory-boy factories (in model_factories modules) and freezegun when applicable
- use `with patch_rules(...)` to test perms

Most tests look something like this:

```
def test_something(vanilla_user_client):
    some_record = Foo.objects.create(...)
    url = reverse("foo", args=[some_record.id])
    with patch_rules(can_access_foo=False):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 403
    with patch_rules(can_access_foo=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
```

See existing tests for examples before writing new ones

Tests can be run

- global `python server/manage.py test server/`
- specific files `python server/manage.py test server/tests/test_foo.py`
- single funcs `python server/manage.py test server/tests/test_foo.py::test_bar`

# Formatting

We use black/isort/djlint to format .py/.jinja2. It can be run globally, but preferably with relevant file arguments. These must run from project root:

1. `isort server/`
2. `black server/`
3. `djlint --reformat server/`

# Behavior instructions

- Prefer working minimal solutions
- Dont go beyond what was requested
- When in doubt look for similar examples in the repo
- Follow existing patterns
