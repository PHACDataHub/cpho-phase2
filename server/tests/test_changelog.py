from unittest.mock import patch

from django.urls import reverse

from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, DimensionValue, Period


def create_versions():
    i1 = IndicatorFactory()
    i2 = IndicatorFactory()
    p1 = Period.objects.first()
    p2 = Period.objects.last()

    s_cat = DimensionType.objects.get(code="sex")
    m_val = s_cat.possible_values.get(value="m")
    f_val = s_cat.possible_values.get(value="f")

    i1.data.create(
        period=p1, dimension_type=s_cat, dimension_value=m_val, value=1
    )
    i1.data.create(
        period=p2, dimension_type=s_cat, dimension_value=m_val, value=2
    )
    i1.data.create(
        period=p1, dimension_type=s_cat, dimension_value=f_val, value=3
    )
    i1.data.create(
        period=p2, dimension_type=s_cat, dimension_value=f_val, value=4
    )
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


def test_changelog(vanilla_user_client):
    create_versions()

    with patch(
        "cpho.views.changelog.GlobalChangelog.get_page_size", lambda _: 2
    ):
        resp = vanilla_user_client.get(reverse("global_changelog"))
        assert resp.status_code == 200
        assert resp.context["num_pages"] > 4
        assert resp.context["page_num"] == 1

        resp = vanilla_user_client.get(
            reverse("global_changelog", kwargs={"page_num": 2})
        )
        assert resp.status_code == 200

        resp = vanilla_user_client.get(
            reverse("global_changelog", kwargs={"page_num": 4})
        )
