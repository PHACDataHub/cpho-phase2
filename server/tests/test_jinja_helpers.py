import os
from unittest import mock

from cpho.jinja_helpers import convert_url_other_lang


def test_convert_url_other_lang():
    environ_without_script_name = {
        k: v for k, v in os.environ.items() if k not in "SCRIPT_NAME"
    }
    with mock.patch.dict(os.environ, environ_without_script_name, clear=True):
        assert convert_url_other_lang("/some/path") == "/fr-ca/some/path"

        assert (
            convert_url_other_lang("/login?next=/some/path")
            == "/fr-ca/login?next=/fr-ca/some/path"
        )

        assert convert_url_other_lang("/fr-ca/some/path") == "/some/path"

        assert (
            convert_url_other_lang("/fr-ca/login?next=/fr-ca/some/path")
            == "/login?next=/some/path"
        )


def test_convert_url_other_lang_with_script_name_env_var():
    with mock.patch.dict(os.environ, {"SCRIPT_NAME": "/test"}):
        assert (
            convert_url_other_lang("/test/some/path")
            == "/test/fr-ca/some/path"
        )

        assert (
            convert_url_other_lang("/test/login?next=/test/some/path")
            == "/test/fr-ca/login?next=/test/fr-ca/some/path"
        )

        assert (
            convert_url_other_lang("/test/fr-ca/some/path")
            == "/test/some/path"
        )

        assert (
            convert_url_other_lang(
                "/test/fr-ca/login?next=/test/fr-ca/some/path"
            )
            == "/test/login?next=/test/some/path"
        )
