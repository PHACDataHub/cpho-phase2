from django.test import override_settings

from server.auth_backend import OAuthBackend

from cpho.models import User


def test_new_user_creates_account():
    backend = OAuthBackend()
    user = backend.authenticate(
        None,
        {"oid": "1234", "email": "abC@phac-aspc.Gc.Ca", "name": "abc def"},
    )
    assert user is not None
    pk = user.pk
    refetched_record = User.objects.get(pk=pk)
    assert refetched_record.username == "1234"
    assert refetched_record.email == "abc@phac-aspc.gc.ca"
    assert refetched_record.name == "abc def"


def test_new_user_healthcan():
    backend = OAuthBackend()
    user = backend.authenticate(
        None, {"oid": "1234", "email": "abC@hc-sc.gc.ca", "name": "abc def"}
    )
    assert user is not None
    pk = user.pk
    refetched_record = User.objects.get(pk=pk)
    assert refetched_record.username == "1234"
    assert refetched_record.email == "abc@hc-sc.gc.ca"
    assert refetched_record.name == "abc def"


def test_new_user_non_allowed_email_rejected():
    backend = OAuthBackend()
    user = backend.authenticate(
        None, {"oid": "1234", "email": "abC@canada.ca", "name": "abc def"}
    )
    assert user is None

    user = backend.authenticate(
        None, {"oid": "1234", "email": "abC@tbs-sct.gc.ca", "name": "abc def"}
    )
    assert user is None


def test_existing_email_uses_existing_account():
    backend = OAuthBackend()
    existing_user = User.objects.create(
        username="abC@deF.com", email="abC@deF.cOm"
    )
    user = backend.authenticate(
        None, {"oid": "1234", "email": "aBc@Def.Com", "name": "abc def"}
    )
    assert user is not None
    assert user.pk == existing_user.pk

    existing_user.refresh_from_db()
    assert existing_user.username == "1234"
    assert existing_user.email == "abc@def.com"
    assert existing_user.name == "abc def"


@override_settings(DISABLE_AUTO_REGISTRATION=True)
def test_new_user_does_not_create_account_when_flag_enabled():
    backend = OAuthBackend()
    user = backend.authenticate(
        None,
        {"oid": "1234", "email": "abC@phac-aspc.Gc.Ca", "name": "abc def"},
    )
    assert user is None
    assert not User.objects.filter(
        email__icontains="abC@phac-aspc.Gc.Ca"
    ).exists()


@override_settings(DISABLE_AUTO_REGISTRATION=False)
def test_new_user_is_created_account_when_flag_disabled():
    backend = OAuthBackend()
    user = backend.authenticate(
        None,
        {"oid": "1234", "email": "abC@phac-aspc.Gc.Ca", "name": "abc def"},
    )
    assert user is not None
    assert User.objects.filter(email__icontains="abC@phac-aspc.Gc.Ca").exists()
