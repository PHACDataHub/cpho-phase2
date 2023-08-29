from django.urls import reverse

from cpho.models import PhacOrgRole, User
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
            "is_account_manager": True,
        }
        resp = vanilla_user_client.post(url, data=data)
        assert resp.status_code == 302
        assert resp.url == reverse("manage_users")
        new_roles = PhacOrgRole.objects.filter(user=u)
        assert {r.phac_org for r in new_roles} == {emb_org}
        assert set(u.groups.all()) == {GroupFetcher.account_manager_group}


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
        "is_account_manager": True,
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
    assert set(user.groups.all()) == {GroupFetcher.account_manager_group}
