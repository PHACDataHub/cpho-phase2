from collections import defaultdict

from django.utils.translation import get_language

import pytz

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
