from collections import defaultdict
from functools import lru_cache

from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import get_language

import pytz

from cpho.constants import ADMIN_GROUP_NAME, HSO_GROUP_NAME
from cpho.text import tdt, tm

eastern_timezone = pytz.timezone("Canada/Eastern")


def get_lang_code():
    lang_locale = get_language()
    if "-ca" not in lang_locale:
        raise Exception("Unexpected language locale: {}".format(lang_locale))
    return lang_locale.split("-ca")[0]


def group_by(iterable, key):
    groups = defaultdict(list)
    for item in iterable:
        groups[key(item)].append(item)
    return groups


flatten = lambda l: [item for sublist in l for item in sublist]


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class GroupFetcher:
    @classproperty
    @lru_cache
    def admin_group(cls):
        return Group.objects.get_or_create(name=ADMIN_GROUP_NAME)[0]

    @classproperty
    @lru_cache
    def hso_group(cls):
        return Group.objects.get_or_create(name=HSO_GROUP_NAME)[0]


def get_or_create_user_by_email(email: str):
    from cpho.models import User

    if not email.endswith("@phac-aspc.gc.ca"):
        raise Exception("Only PHAC emails can be used to register")

    user = User.objects.filter(Q(email__iexact=email)).first()
    if not user:
        user = User.objects.create_user(username=email, email=email)
    return user


phac_email_widget_attrs = {
    # Only allow emails ending in @*.gc.ca or @canada.ca
    "pattern": r"^[a-zA-Z0-9_.+\-]+@([a-zA-Z0-9\-]+\.gc\.ca|canada\.ca)$",
    "oninvalid": f"setCustomValidity('{tm('invalid_email')}')",
    "oninput": "setCustomValidity('')",
    "class": "form-control",
}
