from unittest.mock import patch

from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import (
    BenchmarkingFactory,
    IndicatorFactory,
    TrendAnalysisFactory,
)
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatumHistory,
    IndicatorHistory,
    Period,
    User,
)


def create_versions():
    i1 = IndicatorFactory(name="i1")
    i2 = IndicatorFactory()
    p1 = Period.objects.first()
    p2 = Period.objects.last()

    def add_datum_version(datum, value):
        datum.reset_version_attrs()
        datum.value = value
        datum.save()

    s_cat = DimensionType.objects.get(code="sex")
    m_val = s_cat.possible_values.get(value="m")
    f_val = s_cat.possible_values.get(value="f")

    i1_d1 = i1.data.create(
        period=p1, dimension_type=s_cat, dimension_value=m_val, value=1
    )
    add_datum_version(i1_d1, 1.1)
    i1_d2 = i1.data.create(
        period=p2, dimension_type=s_cat, dimension_value=m_val, value=2
    )
    add_datum_version(i1_d2, 2.2)
    i1.data.create(
        period=p1, dimension_type=s_cat, dimension_value=f_val, value=3
    )
    i1_d4 = i1.data.create(
        period=p2, dimension_type=s_cat, dimension_value=f_val, value=4
    )
    add_datum_version(i1_d4, 4.4)
    i2.data.create(
        period=p1, dimension_type=s_cat, dimension_value=m_val, value=5
    )
    i2.data.create(
        period=p2, dimension_type=s_cat, dimension_value=m_val, value=6
    )
    i2.data.create(
        period=p1, dimension_type=s_cat, dimension_value=f_val, value=7
    )
    i2.data.create(
        period=p2, dimension_type=s_cat, dimension_value=f_val, value=8
    )

    # also create some benchmarking and trend analysis
    bm1 = BenchmarkingFactory(indicator=i1, value=1)
    bm1.reset_version_attrs()
    bm1.value = 1.1
    bm1.save()

    bm2 = BenchmarkingFactory(value=2, indicator=i2)
    bm2.reset_version_attrs()
    bm2.value = 2.2
    bm2.save()

    ta1 = TrendAnalysisFactory(indicator=i1, data_point=1)
    ta1.reset_version_attrs()
    ta1.data_point = 1.1
    ta1.save()

    ta2 = TrendAnalysisFactory(indicator=i2, data_point=2)
    ta2.reset_version_attrs()
    ta2.data_point = 2.2
    ta2.save()


def test_global_changelog(vanilla_user_client):
    create_versions()

    if settings.USE_SQLITE:
        print("skipping changelog test because sqlite is used")
        return

    with patch_rules(is_admin_or_hso=False):
        resp = vanilla_user_client.get(reverse("global_changelog"))
        assert resp.status_code == 403

    with (
        patch_rules(is_admin_or_hso=True),
        patch("cpho.views.changelog.ChangelogView.get_page_size", lambda _: 2),
    ):
        resp = vanilla_user_client.get(reverse("global_changelog"))
        assert resp.status_code == 200
        assert resp.context["num_pages"] == 11
        assert resp.context["page_num"] == 1

        resp = vanilla_user_client.get(
            reverse("global_changelog", kwargs={"page_num": 2})
        )
        assert resp.status_code == 200

        resp = vanilla_user_client.get(
            reverse("global_changelog", kwargs={"page_num": 4})
        )


def test_indicator_changelog(vanilla_user_client):
    create_versions()
    i1 = Indicator.objects.first()

    if settings.USE_SQLITE:
        print("skipping changelog test because sqlite is used")
        return

    with patch_rules(can_access_indicator=False):
        resp = vanilla_user_client.get(
            reverse(
                "indicator_scoped_changelog", kwargs={"indicator_id": i1.id}
            )
        )
        assert resp.status_code == 403

    with (
        patch_rules(can_access_indicator=True),
        patch(
            "cpho.views.changelog.ChangelogView.get_page_size",
            lambda _: 2,
        ),
    ):
        resp = vanilla_user_client.get(
            reverse(
                "indicator_scoped_changelog", kwargs={"indicator_id": i1.id}
            )
        )
        assert resp.status_code == 200
        assert resp.context["num_pages"] == 6
        assert resp.context["page_num"] == 1

        resp = vanilla_user_client.get(
            reverse(
                "indicator_scoped_changelog",
                kwargs={"indicator_id": i1.id, "page_num": 2},
            )
        )
        assert resp.status_code == 200

        resp = vanilla_user_client.get(
            reverse(
                "indicator_scoped_changelog",
                kwargs={"indicator_id": i1.id, "page_num": 4},
            )
        )


def test_user_scoped_changelog(vanilla_user, vanilla_user_client):
    other_user = User.objects.create(username="other")
    other_user_client = Client()
    other_user_client.force_login(other_user)

    u_id = vanilla_user.id
    create_versions()
    IndicatorHistory.objects.filter(name="i1").update(edited_by_id=u_id)
    IndicatorDatumHistory.objects.filter(indicator__name="i1").update(
        edited_by_id=u_id
    )

    if settings.USE_SQLITE:
        print("skipping changelog test because sqlite is used")
        return

    # Test that a user can't access another user's changelog
    resp = vanilla_user_client.get(
        reverse("user_scoped_changelog", kwargs={"user_id": other_user.id})
    )
    assert resp.status_code == 403

    # unless they are super user
    with patch_rules(is_admin_or_hso=True):
        resp = vanilla_user_client.get(
            reverse("user_scoped_changelog", kwargs={"user_id": other_user.id})
        )
        assert resp.status_code == 200

    # now test actual behaviour
    with patch(
        "cpho.views.changelog.ChangelogView.get_page_size",
        lambda _: 2,
    ):
        resp = vanilla_user_client.get(
            reverse("user_scoped_changelog", kwargs={"user_id": u_id})
        )
        assert resp.status_code == 200
        assert resp.context["num_pages"] == 4
        assert resp.context["page_num"] == 1

        resp = vanilla_user_client.get(
            reverse(
                "user_scoped_changelog",
                kwargs={
                    "user_id": u_id,
                    "page_num": 2,
                },
            )
        )
        assert resp.status_code == 200

        resp = vanilla_user_client.get(
            reverse(
                "user_scoped_changelog",
                kwargs={
                    "user_id": u_id,
                    "page_num": 4,
                },
            )
        )


def test_datum_changelog(vanilla_user_client):
    if settings.USE_SQLITE:
        print("skipping changelog test because sqlite is used")
        return

    year = Period.objects.first().year

    create_versions()

    with patch_rules(is_admin_or_hso=False):
        resp = vanilla_user_client.get(reverse("global_datum_changelog"))
        assert resp.status_code == 403

    with (
        patch_rules(is_admin_or_hso=True),
        patch("cpho.views.changelog.ChangelogView.get_page_size", lambda _: 2),
    ):
        resp = vanilla_user_client.get(reverse("global_datum_changelog"))
    assert resp.status_code == 200

    url_with_year_param = reverse("global_datum_changelog") + "?year=1999"
    with (
        patch_rules(is_admin_or_hso=True),
        patch("cpho.views.changelog.ChangelogView.get_page_size", lambda _: 2),
    ):
        resp_with_year_param = vanilla_user_client.get(url_with_year_param)
    assert resp_with_year_param.status_code == 200
    assert len(resp_with_year_param.context["edit_entries"]) == 0

    url_with_year_param = reverse("global_datum_changelog") + f"?year={year}"
    with (
        patch_rules(is_admin_or_hso=True),
        patch("cpho.views.changelog.ChangelogView.get_page_size", lambda _: 2),
    ):
        resp_with_year_param = vanilla_user_client.get(url_with_year_param)
    assert resp_with_year_param.status_code == 200
    assert len(resp_with_year_param.context["edit_entries"]) == 2
