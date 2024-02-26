from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorFactory
from cpho.models import (
    IndicatorDirectory,
    IndicatorDirectoryLink,
    IndicatorDirectoryUserAccess,
    User,
)
from cpho.util import GroupFetcher


def test_list_users(vanilla_user_client):
    url = reverse("manage_users")
    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200


def test_modify_user(vanilla_user_client):
    u = User.objects.create(email="test@canada.ca")
    u.groups.add(GroupFetcher.admin_group)

    url = reverse("modify_user", args=[u.id])

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200

        data = {
            # ommission of is_admin should imply false
            "is_admin": True,
        }
        resp = vanilla_user_client.post(url, data=data)
        assert resp.status_code == 302
        assert resp.url == reverse("manage_users")
        assert set(u.groups.all()) == {GroupFetcher.admin_group}


def test_create_user(vanilla_user_client):
    url = reverse("create_user")

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)

    assert resp.status_code == 200

    email = "testy@phac-aspc.gc.ca"
    data = {
        "email": email,
        "email_confirmation": email,
        "is_hso": True,
    }
    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.post(url, data=data)

    assert resp.status_code == 302
    user = User.objects.get(email=email)
    assert user.username == email
    assert set(user.groups.all()) == {GroupFetcher.hso_group}


def test_create_indicator_directory(vanilla_user_client):
    i1 = IndicatorFactory()
    i2 = IndicatorFactory()
    i3 = IndicatorFactory()
    u1 = User.objects.create(username="test1")
    u2 = User.objects.create(username="test2")
    u3 = User.objects.create(username="test3")

    url = reverse("create_indicator_directory")

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
    assert resp.status_code == 200

    data = {
        "name": "test directory",
        "description": "test description",
        "indicators": [i1.id, i2.id],
        "users": [u1.id, u2.id],
    }
    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.post(url, data=data)

    assert resp.status_code == 302
    assert resp.url == reverse("root")

    directory = IndicatorDirectory.objects.get(name="test directory")
    assert set(directory.users.all()) == {u1, u2}
    assert set(directory.indicators.all()) == {i1, i2}

    assert IndicatorDirectoryUserAccess.objects.all().count() == 2
    assert IndicatorDirectoryLink.objects.all().count() == 2


def test_edit_indicator_directory(vanilla_user_client):
    i1 = IndicatorFactory()
    i2 = IndicatorFactory()
    i3 = IndicatorFactory()
    u1 = User.objects.create(username="test1")
    u2 = User.objects.create(username="test2")
    u3 = User.objects.create(username="test3")

    directory = IndicatorDirectory.objects.create(
        name="test directory", description="test description"
    )
    directory.users.add(u1)
    directory.users.add(u2)
    directory.indicators.add(i1)
    directory.indicators.add(i2)

    url = reverse("edit_indicator_directory", args=[directory.id])

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
    assert resp.status_code == 200

    data = {
        "name": "new name",
        "description": "new description",
        "indicators": [i1.id, i3.id],
        "users": [u1.id, u3.id],
    }
    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.post(url, data=data)

    assert resp.status_code == 302
    assert resp.url == reverse("root")

    directory.refresh_from_db()
    assert directory.name == "new name"
    assert directory.description == "new description"

    assert set(directory.users.all()) == {u1, u3}
    assert set(directory.indicators.all()) == {i1, i3}


def test_indicator_directory_home(vanilla_user, vanilla_user_client):
    i1 = IndicatorFactory()
    dir = IndicatorDirectory.objects.create(
        name="test directory", description="test description"
    )
    dir.indicators.add(i1)

    url = reverse("indicator_directory_home", args=[dir.id])
    assert vanilla_user_client.get(url).status_code == 403

    dir.users.add(vanilla_user)
    assert vanilla_user_client.get(url).status_code == 200

    # now try adding new users

    # 1. an invalid email
    resp = vanilla_user_client.post(url, data={"email": "invalid@xyz.com"})
    assert resp.status_code == 200
    assert "email" in resp.context["form"].errors

    # 2. a brand new user
    resp = vanilla_user_client.post(
        url,
        data={
            "email": "billy.bob@phac-aspc.gc.ca",
            "email_confirmation": "billy.bob@phac-aspc.gc.ca",
        },
    )
    assert resp.status_code == 302
    assert resp.url == reverse("indicator_directory_home", args=[dir.id])
    assert dir.users.filter(email="billy.bob@phac-aspc.gc.ca").exists()

    # 3. an existing user
    new_user = User.objects.create(email="testy.testerton@phac-aspc.gc.ca")
    resp = vanilla_user_client.post(
        url,
        data={"email": new_user.email, "email_confirmation": new_user.email},
    )
    assert resp.status_code == 302
    assert dir.users.filter(email="testy.testerton@phac-aspc.gc.ca").exists()
