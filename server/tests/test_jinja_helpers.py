from cpho.jinja_helpers import convert_url_other_lang


def test_convert_url_other_lang():
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
