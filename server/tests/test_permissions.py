from django.urls import reverse

from server.rules_framework import test_rule as tr

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDirectory,
    Period,
    PHACOrg,
    User,
)
from cpho.queries import get_indicators_for_user


def _test_permissions(
    cdsb_user_client,
    cdsb_user,
    cdsb_lead_client,
    cdsb_lead,
    hso_client,
    hso_user,
    oae_lead_client,
    oae_lead,
):
    url = reverse("create_indicator")

    # Program User should not be able to create indicator
    resp = cdsb_user_client.get(url)
    assert resp.status_code == 403
    # assert tr("can_create_indicator", cdsb_user) is False

    cdsb_phacOrg = PHACOrg.objects.get(acronym_en="CDSB").id
    response = cdsb_user_client.post(
        url,
        data={
            "name": "Test Indicator",
            "category": Indicator.CATEGORY_CHOICES[-1][0],
            "topic": Indicator.TOPIC_CHOICES[-1][0],
            "detailed_indicator": "Test Detailed Indicator",
            "sub_indicator_measurement": "Test Sub Indicator Measurement",
            "PHACOrg": cdsb_phacOrg,
        },
    )
    assert response.status_code == 403

    # Program Lead User not should be able to create indicator
    resp = cdsb_lead_client.get(url)
    assert resp.status_code == 403
    assert tr("can_create_indicator", cdsb_lead) is False

    response = cdsb_lead_client.post(
        url,
        data={
            "name": "Test Indicator",
            "category": Indicator.CATEGORY_CHOICES[-1][0],
            "topic": Indicator.TOPIC_CHOICES[-1][0],
            "detailed_indicator": "Test Detailed Indicator",
            "sub_indicator_measurement": "Test Sub Indicator Measurement",
            "PHACOrg": cdsb_phacOrg,
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
            "PHACOrg": cdsb_phacOrg,
        },
    )
    assert r.status_code == 302
    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"

    # only hso, CDSB user and lead should be able to view this indicator as they are the PHACOrg for this indicator
    indicator_pk = indicator.pk
    indicator = Indicator.objects.get(pk=indicator_pk)
    url = reverse("view_indicator", kwargs={"pk": indicator_pk})
    assert tr("can_access_indicator", cdsb_user, indicator) is True
    assert tr("can_access_indicator", cdsb_lead, indicator) is True
    assert tr("can_access_indicator", hso_user, indicator) is True
    assert tr("can_access_indicator", oae_lead, indicator) is False

    resp = cdsb_user_client.get(url)
    assert resp.status_code == 200
    resp = cdsb_lead_client.get(url)
    assert resp.status_code == 200
    resp = hso_client.get(url)
    assert resp.status_code == 200
    resp = oae_lead_client.get(url)
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

    # only hso, CDSB user and CDSB lead should be able to view indicator datum.
    assert tr("can_access_indicator", cdsb_user, indicator) is True
    assert tr("can_access_indicator", cdsb_lead, indicator) is True
    assert tr("can_access_indicator", hso_user, indicator) is True
    assert tr("can_access_indicator", oae_lead, indicator) is False

    url = reverse(
        "view_indicator_for_period",
        kwargs={
            "pk": indicator_pk,
            "period_pk": period.id,
        },
    )
    resp = cdsb_user_client.get(url)
    assert resp.status_code == 200

    resp = cdsb_lead_client.get(url)
    assert resp.status_code == 200

    resp = hso_client.get(url)
    assert resp.status_code == 200

    resp = oae_lead_client.get(url)
    assert resp.status_code == 403

    # only hso, and CDSB lead should be able to edit indicator datum.
    assert tr("can_access_indicator", cdsb_user, indicator) is False
    assert tr("can_access_indicator", cdsb_lead, indicator) is True
    assert tr("can_access_indicator", hso_user, indicator) is True
    assert tr("can_access_indicator", oae_lead, indicator) is False
    url = reverse(
        "manage_indicator_data",
        kwargs={
            "indicator_id": indicator_pk,
            "period_pk": period.id,
            "dimension_type_id": sex_dim_type.id,
        },
    )
    resp = cdsb_lead_client.get(url)
    assert resp.status_code == 200

    resp = hso_client.get(url)
    assert resp.status_code == 200

    resp = oae_lead_client.get(url)
    assert resp.status_code == 403

    resp = cdsb_user_client.get(url)
    assert resp.status_code == 403

    # only CDSB lead and hso should be able to submit indicator datum.
    assert tr("can_submit_indicator", cdsb_user, indicator) is False
    assert tr("can_submit_indicator", cdsb_lead, indicator) is True
    assert tr("can_submit_indicator", hso_user, indicator) is True
    assert tr("can_submit_indicator", oae_lead, indicator) is False
    url = reverse(
        "submit_indicator_data",
        kwargs={
            "indicator_id": indicator_pk,
            "period_pk": period.id,
            "dimension_type_id": sex_dim_type.id,
        },
    )

    resp = cdsb_user_client.post(url, {"submission_type": "program"})
    assert resp.status_code == 403

    resp = oae_lead_client.post(url, {"submission_type": "program"})
    assert resp.status_code == 403

    resp = cdsb_lead_client.post(url, {"submission_type": "program"})
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
