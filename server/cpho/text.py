from django.utils.functional import lazy
from django.utils.html import mark_safe
from django.utils.translation import get_language, get_language_info

from cpho.translations import translation_entries

lang_map = {
    "en": "en",
    "fr": "fr",
    "fallback": "fr_auto",
}

RAISE_ON_MISSING_KEY = True
RAISE_ON_MISSING_LANG = False


def get_language_code(lang=None):
    """Translate strings like fr-ca, en-ca to fr and en respectively
    If lang is not specified the current active language will be used.
    """
    if not lang:
        lang = get_language()
    try:
        return get_language_info(lang)["code"]
    except TypeError:
        return "en"


def other_lang():
    """Returns the 2 letter acronym of the language the user is NOT using"""
    if get_language_code() == "en":
        return "fr"
    return "en"


def tdt(s: str):
    return s


def tm(key: str) -> str:
    """Wrapper around translation dictionary lookups"""
    text = translation_entries.get(key.lower())

    if text is None:
        if RAISE_ON_MISSING_KEY:
            raise Exception("missing  key: " + key)
        return f"Missing **{key}** key"

    lang_code = get_language_code() or "en"
    # French fallback to machine translation if the string is not yet translated
    FALLBACK_FLAG = True  # Set to False to disable fallback
    if lang_code == "fr" and FALLBACK_FLAG:
        if text.get(lang_map.get(lang_code)) is None:
            lang_code = "fallback"
    locale_string = text.get(lang_map.get(lang_code))

    if locale_string is not None:
        return locale_string

    if RAISE_ON_MISSING_LANG:
        raise Exception(f"missing translation for {key} in {lang_code}")
    else:
        return f"Missing **{key}[{lang_map[lang_code]}]**"


tm = lazy(tm, str)
