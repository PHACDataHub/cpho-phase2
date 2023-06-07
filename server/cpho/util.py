from django.utils.translation import get_language


def get_lang_code():
    lang_locale = get_language()
    if "-ca" not in lang_locale:
        raise Exception("Unexpected language locale: {}".format(lang_locale))
    return lang_locale.split("-ca")[0]
