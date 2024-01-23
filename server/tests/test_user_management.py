from django.urls import reverse

from cpho.model_factories import IndicatorFactory
from cpho.models import (
    IndicatorDirectory,
    IndicatorDirectoryLink,
    IndicatorDirectoryUserAccess,
    PhacOrgRole,
    User,
)
from cpho.util import GroupFetcher

from .utils_for_tests import patch_rules


def test_list_users(vanilla_user_client):
    url = reverse("manage_users")
    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
        assert resp.context["user_metadata"]


def test_modify_user(vanilla_user_client, cdsb_org, emb_org):
    u = User.objects.create(email="test@canada.ca")
    PhacOrgRole.objects.create(user=u, phac_org=cdsb_org)
    u.groups.add(GroupFetcher.admin_group)

    url = reverse("modify_user", args=[u.id])

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200

        data = {
            "phac_org_multi": [emb_org.id],  # delete cdsb, add cira
            # ommission of is_admin should imply false
            "is_admin": True,
        }
        resp = vanilla_user_client.post(url, data=data)
        assert resp.status_code == 302
        assert resp.url == reverse("manage_users")
        new_roles = PhacOrgRole.objects.filter(user=u)
        assert {r.phac_org for r in new_roles} == {emb_org}
        assert set(u.groups.all()) == {GroupFetcher.admin_group}


def test_create_user(vanilla_user_client, cdsb_org, emb_org):
    url = reverse("create_user")

    unauth_resp = vanilla_user_client.get(url)
    assert unauth_resp.status_code == 403

    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.get(url)

    assert resp.status_code == 200

    email = "testy@phac-aspc.gc.ca"
    data = {
        "email": email,
        "phac_org_multi": [cdsb_org.id, emb_org.id],
        "is_hso": True,
    }
    with patch_rules(can_manage_users=True):
        resp = vanilla_user_client.post(url, data=data)

    assert resp.status_code == 302
    user = User.objects.get(email=email)
    assert user.username == email
    assert {r.phac_org for r in user.phac_org_roles.all()} == {
        emb_org,
        cdsb_org,
    }
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
