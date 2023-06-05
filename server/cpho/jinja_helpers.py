from urllib.parse import quote, urlencode, urlparse, urlunparse

from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import activate, get_language

import phac_aspc.django.helpers.templatetags as phac_aspc
from jinja2 import Environment, pass_context

from cpho import models

from .text import tdt, tm


def convert_url_other_lang(url_str):
    parsed_url = urlparse(url_str)
    path = parsed_url.path
    query = parsed_url.query

    if "fr-ca" in path:
        new_path = path.replace("/fr-ca", "")
    else:
        new_path = "/fr-ca" + path

    new_url = parsed_url._replace(path=new_path)

    if "login" in path and "next" in query:
        if "fr-ca" in path:
            new_query = query.replace("next=/fr-ca", "next=")
        else:
            new_query = query.replace("next=", "next=/fr-ca")
    else:
        new_query = query

    new_url = new_url._replace(query=new_query)

    return urlunparse(new_url)


@pass_context
def url_to_other_lang(context):
    """
    Provides the URL to the other language:
    For example, if current language is English then it will provide
    the url to the French language.
    """
    request = context["request"]
    full_uri = request.get_full_path()
    return convert_url_other_lang(full_uri)


def get_other_lang_code():
    """
    Provides the language code for the other language (Ex. if current lang
    is en-ca, then the other lang is fr-ca), this is currently used for
    setting the lang tag in the button switch UI
    """
    current_lang = get_language()
    if "en" in current_lang.lower():
        return "fr-ca"
    return "en-ca"


def get_other_lang():
    """
    Returns the language not currently being used (Ex. if current lang
    is en, then the other lang is French.  This is used as the label for the
    button to switch languages)
    """
    current_lang = get_language()
    if "en" in current_lang.lower():
        return "Français"
    return "English"


def message_type(message):
    # remaps the message level tag to the bootstrap alert type
    if message.level_tag == "error":
        return "danger"
    else:
        return f"{message.level_tag}"


@pass_context
def ipython(context):
    from IPython import embed

    embed()
    return ""


def message_type(message):
    # remaps the message level tag to the bootstrap alert type
    if message.level_tag == "error":
        return "danger"
    else:
        return f"{message.level_tag}"


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "getattr": getattr,
            "hasattr": hasattr,
            "len": len,
            "list": list,
            "url": reverse,
            "url_to_other_lang": url_to_other_lang,
            "get_other_lang_code": get_other_lang_code,
            "get_other_lang": get_other_lang,
            "get_lang": get_language,
            "urlencode": urlencode,
            "static": static,
            "phac_aspc": phac_aspc,
            "message_type": message_type,
            "ipython": ipython,
            "tm": tm,
            "tdt": tdt,
            "message_type": message_type,
            "print": print,
            "cpho_models": models,
        }
    )
    env.filters["quote"] = lambda x: quote(str(x))
    return env
