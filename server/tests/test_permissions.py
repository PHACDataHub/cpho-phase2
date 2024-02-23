from django.test.client import Client
from django.urls import reverse

from phac_aspc.rules import test_rule as tr

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDirectory,
    Period,
    User,
)
from cpho.queries import get_indicators_for_user


def test_create_indicator_authorization(
    hso_user, hso_client, vanilla_user, vanilla_user_client
):
    url = reverse("create_indicator")

    # Non admins/hso should not be able to create indicator
    resp = vanilla_user_client.get(url)
    assert resp.status_code == 403
    assert tr("can_create_indicator", vanilla_user) is False

    response = vanilla_user_client.post(
        url,
        data={
            "name": "Test Indicator",
            "category": Indicator.CATEGORY_CHOICES[-1][0],
            "topic": Indicator.TOPIC_CHOICES[-1][0],
            "detailed_indicator": "Test Detailed Indicator",
            "sub_indicator_measurement": "Test Sub Indicator Measurement",
        },
    )
    assert response.status_code == 403

    # HSO User should be able to create indicator
    resp = hso_client.get(url)
    assert resp.status_code == 200
    assert tr("can_create_indicator", hso_user) is True

    r = hso_client.post(
        url,
        data={
            "name": "Test Indicator",
            "category": Indicator.CATEGORY_CHOICES[-1][0],
            "topic": Indicator.TOPIC_CHOICES[-1][0],
            "detailed_indicator": "Test Detailed Indicator",
            "sub_indicator_measurement": "Test Sub Indicator Measurement",
        },
    )
    assert r.status_code == 302
    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"


def test_indicator_authorization(hso_user, hso_client):
    user = User.objects.create(username="main")
    user_client = Client()
    user_client.force_login(user)
    other_user = User.objects.create(username="other")
    other_user_client = Client()
    other_user_client.force_login(other_user)

    dir = IndicatorDirectory.objects.create(name="dir")
    indicator = IndicatorFactory()
    dir.indicators.add(indicator)
    dir.users.add(user)

    # only hso, CDSB user and lead should be able to view this indicator as they are the PHACOrg for this indicator
    indicator = Indicator.objects.get(pk=indicator.pk)

    assert tr("can_access_indicator", user, indicator)
    assert tr("can_access_indicator", hso_user, indicator)
    assert not tr("can_access_indicator", other_user, indicator)

    url = reverse("view_indicator", kwargs={"pk": indicator.pk})

    resp = user_client.get(url)
    assert resp.status_code == 200

    resp = hso_client.get(url)
    assert resp.status_code == 200

    resp = other_user_client.get(url)
    assert resp.status_code == 403

    # fill in indicator data for sex dimension this indicator

    sex_dim_type = DimensionType.objects.get(code="sex")
    period = Period.objects.last()
    possible_dimension_value = sex_dim_type.possible_values.all()
    datum = IndicatorDatumFactory(
        indicator=indicator,
        dimension_value=possible_dimension_value[0],
        period=period,
        dimension_type=sex_dim_type,
    )
    datum.save()
    datum = IndicatorDatumFactory(
        indicator=indicator,
        dimension_value=possible_dimension_value[1],
        period=period,
        dimension_type=sex_dim_type,
    )
    datum.save()

    url = reverse(
        "view_indicator_for_period",
        kwargs={
            "pk": indicator.pk,
            "period_pk": period.id,
        },
    )
    resp = user_client.get(url)
    assert resp.status_code == 200

    resp = hso_client.get(url)
    assert resp.status_code == 200

    resp = other_user_client.get(url)
    assert resp.status_code == 403

    url = reverse(
        "manage_indicator_data",
        kwargs={
            "indicator_id": indicator.pk,
            "period_pk": period.id,
            "dimension_type_id": sex_dim_type.id,
        },
    )
    assert user_client.get(url).status_code == 200

    assert hso_client.get(url).status_code == 200

    assert other_user_client.get(url).status_code == 403

    # only CDSB lead and hso should be able to submit indicator datum.
    assert tr("can_submit_indicator", user, indicator)
    assert tr("can_submit_indicator", hso_user, indicator)
    assert not tr("can_submit_indicator", other_user, indicator)
    url = reverse(
        "submit_indicator_data",
        kwargs={
            "indicator_id": indicator.pk,
            "period_pk": period.id,
            "dimension_type_id": sex_dim_type.id,
        },
    )

    resp = other_user_client.post(url, {"submission_type": "program"})
    assert resp.status_code == 403

    resp = user_client.post(url, {"submission_type": "program"})
    assert resp.status_code == 302

    resp = hso_client.post(url, {"submission_type": "hso"})
    assert resp.status_code == 302


def test_indicator_authorization_rule(hso_user):
    i1 = IndicatorFactory()
    i2 = IndicatorFactory()
    i3 = IndicatorFactory()

    assert tr("can_access_indicator", hso_user, i1)

    u1 = User.objects.create(username="u1")
    u2 = User.objects.create(username="u2")
    u3 = User.objects.create(username="u3")

    d1 = IndicatorDirectory.objects.create(name="d1")
    d1.indicators.add(i1, i2)
    d1.users.add(u1, u2)

    d2 = IndicatorDirectory.objects.create(name="d2")
    d2.indicators.add(i3)
    d2.users.add(u2, u3)

    assert tr("can_access_indicator", u1, i1)
    assert tr("can_access_indicator", u1, i2)
    assert not tr("can_access_indicator", u1, i3)
    assert tr("can_access_indicator", u2, i3)

    assert get_indicators_for_user(u1.id) == {i1, i2}
    assert get_indicators_for_user(u2.id) == {i1, i2, i3}
    assert get_indicators_for_user(u3.id) == {i3}
