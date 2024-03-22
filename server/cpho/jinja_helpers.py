import os
from urllib.parse import quote, urlencode, urlparse, urlunparse

from django.apps import apps
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import activate, get_language

import phac_aspc.django.helpers.templatetags as phac_aspc
from jinja2 import Environment, pass_context
from phac_aspc.rules import test_rule

from server.config_util import get_project_config

from cpho import models
from cpho.constants import SUBMISSION_STATUSES
from cpho.util import eastern_timezone

from .text import tdt, tm

config = get_project_config()


def convert_url_other_lang(url_str):
    parsed_url = urlparse(url_str)
    path = parsed_url.path
    query = parsed_url.query

    # SCRIPT_NAME must be set as an os env so gunicorn also sees it. Could
    # access via config(), but don't want to imply it could be set via a .env
    app_root_path = os.getenv("SCRIPT_NAME", "")

    if "fr-ca" in path:
        new_path = path.replace("/fr-ca", "", 1)
    else:
        new_path = path.replace(app_root_path, app_root_path + "/fr-ca", 1)

    new_url = parsed_url._replace(path=new_path)

    if "login" in path and "next" in query:
        if "fr-ca" in path:
            new_query = query.replace(
                "next=" + app_root_path + "/fr-ca", "next=" + app_root_path, 1
            )
        else:
            new_query = query.replace(
                "next=" + app_root_path, "next=" + app_root_path + "/fr-ca", 1
            )
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


def get_lang_code():
    """
    Provides the language code for the current language
    """
    current_lang = get_language()
    return current_lang.lower()


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


@pass_context
def respects_rule(context, rule, obj=None):
    user = context["request"].user
    if not user.is_authenticated:
        return False
    return test_rule(rule, user, obj)


def message_type(message):
    # remaps the message level tag to the bootstrap alert type
    if message.level_tag == "error":
        return "danger"
    else:
        return f"{message.level_tag}"


def submission_status_label(submission_status):
    return {
        SUBMISSION_STATUSES.NO_DATA: tm("no_data"),
        SUBMISSION_STATUSES.NOT_YET_SUBMITTED: tm("not_yet_submitted"),
        SUBMISSION_STATUSES.PROGRAM_SUBMITTED: tm("program_submitted"),
        SUBMISSION_STATUSES.SUBMITTED: tm("submitted_by_program_and_hso"),
        SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION: tm(
            "modified_since_last_submission"
        ),
    }[submission_status]


@pass_context
def with_new_url_kwargs(context, **new_kwargs):
    """
    Uses kwargs from current context and merges new kwargs over them to return a new URL
    """
    request = context["request"]
    new_kwargs = {**request.resolver_match.kwargs, **new_kwargs}
    return reverse(request.resolver_match.url_name, kwargs=new_kwargs)


@pass_context
def with_same_params(context, url):
    """
    Uses GET params from current context and returns a new URL with them

    input url must not have any GET params, or else output will be invalid

    useful for non-querystring-based pagination of a querystring-filtered view
    """

    if not context["request"].GET:
        # dont append a useless '?' if unecessary
        return url

    return f"{url}?{context['request'].GET.urlencode()}"


def vb_name(model_str, field_name):
    return apps.get_model(model_str)._meta.get_field(field_name).verbose_name


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "eastern_timezone": eastern_timezone,
            "getattr": getattr,
            "hasattr": hasattr,
            "len": len,
            "list": list,
            "url": reverse,
            "url_to_other_lang": url_to_other_lang,
            "get_lang_code": get_lang_code,
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
            "print": print,
            "cpho_models": models,
            "test_rule": test_rule,
            "respects_rule": respects_rule,
            "submission_status_label": submission_status_label,
            "SUBMISSION_STATUSES": SUBMISSION_STATUSES,
            "with_new_url_kwargs": with_new_url_kwargs,
            "with_same_params": with_same_params,
            "vb_name": vb_name,
            # global flags:
            "PHAC_ASPC_OAUTH_PROVIDER": config(
                "PHAC_ASPC_OAUTH_PROVIDER", default=None
            ),
            "ENABLE_LEGACY_LOG_IN": config(
                "ENABLE_LEGACY_LOG_IN", cast=bool, default=False
            ),
        }
    )
    env.filters["quote"] = lambda x: quote(str(x))
    return env
