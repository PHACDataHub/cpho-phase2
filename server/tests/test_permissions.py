from cpho.model_factories import IndicatorDatumFactory
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    Period,
    PHACOrg,
)
from django.urls import reverse

from server.rules_framework import test_rule as tr


def test_permissions(
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
    # assert test_rule("can_create_indicator", cdsb_user) is False

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
    assert tr("can_view_indicator", cdsb_user, indicator) is True
    assert tr("can_view_indicator", cdsb_lead, indicator) is True
    assert tr("can_view_indicator", hso_user, indicator) is True
    assert tr("can_view_indicator", oae_lead, indicator) is False

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
    assert tr("can_view_indicator_data", cdsb_user, indicator) is True
    assert tr("can_view_indicator_data", cdsb_lead, indicator) is True
    assert tr("can_view_indicator_data", hso_user, indicator) is True
    assert tr("can_view_indicator_data", oae_lead, indicator) is False

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
    assert tr("can_edit_indicator_data", cdsb_user, indicator) is False
    assert tr("can_edit_indicator_data", cdsb_lead, indicator) is True
    assert tr("can_edit_indicator_data", hso_user, indicator) is True
    assert tr("can_edit_indicator_data", oae_lead, indicator) is False
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
    assert tr("can_submit_as_hso_or_program", cdsb_user, indicator) is False
    assert tr("can_submit_as_hso_or_program", cdsb_lead, indicator) is True
    assert tr("can_submit_as_hso_or_program", hso_user, indicator) is True
    assert tr("can_submit_as_hso_or_program", oae_lead, indicator) is False
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
