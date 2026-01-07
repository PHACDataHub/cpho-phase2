from collections import defaultdict
from functools import lru_cache

from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import get_language

import pytz
from data_fetcher import cache_within_request

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
    @cache_within_request
    def admin_group(cls):
        return Group.objects.get_or_create(name=ADMIN_GROUP_NAME)[0]

    @classproperty
    @cache_within_request
    def hso_group(cls):
        return Group.objects.get_or_create(name=HSO_GROUP_NAME)[0]


def is_allowed_email(email: str):
    return email.lower().endswith(
        "@phac-aspc.gc.ca"
    ) or email.lower().endswith("@hc-sc.gc.ca")


def get_or_create_user_by_email(email: str):
    from cpho.models import User

    if not is_allowed_email(email):
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


def get(obj, attr_path, default=""):
    """
    Get an attribute from an object, but if it's falsey, return None
    """
    value = obj
    for attr in attr_path.split("."):
        value = getattr(value, attr, None)
        if not value:
            return default
    return value


def get_regex_pattern(match_type):
    all_patterns = {
        "benchmarking_year": {
            "pattern": r"^\s*(\d{1,2})\s*\/\s*(\d{4})\s*$",
            "valid": [
                "09/2020",
                "9/2020",
                "09 / 2020",
                "9 / 2020",
                " 9/2020 ",
                " 9 / 2020 ",
            ],
        },
        "trend_year_single": {
            "pattern": r"^\s*(\d{4})\s*$",
            "valid": ["2020", " 2020 ", " 2020", "2020 "],
        },
        "trend_year_multi": {
            "pattern": r"^\s*(\d{4})\s*-\s*(\d{4})\s*$",
            "valid": [
                "2020-2021",
                " 2020 - 2021 ",
                " 2020-2021",
                "2020 - 2021 ",
                "2020 - 2021",
                " 2020 -2021",
            ],
        },
        "trend_segment_single": {
            "pattern": r"^\s*(\d{4})\s*-\s*(\d{4})\s*$",
            "valid": [
                "2020-2021",
                " 2020 - 2021 ",
                " 2020-2021",
                "2020 - 2021 ",
                "2020 - 2021",
                " 2020 -2021",
            ],
        },
        "trend_segment_multi": {
            "pattern": r"^\s*(\d{4})\s*-\s*(\d{4})\s*to\s*(\d{4})\s*-\s*(\d{4})\s*$",
            "valid": [
                "2020-2021 to 2022-2023",
                " 2020 - 2021 to 2022 - 2023 ",
                " 2020-2021 to 2022-2023",
                "2020 - 2021 to 2022 - 2023 ",
                "2020 - 2021 to 2022 - 2023",
                " 2020 -2021 to 2022 -2023",
            ],
        },
    }
    if match_type == "all":
        return all_patterns

    return all_patterns[match_type]
