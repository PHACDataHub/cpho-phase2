from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorFactory
from cpho.models import Indicator


def test_create_indicator(vanilla_user_client):
    url = reverse("create_indicator")
    with patch_rules(can_create_indicator=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

        response = vanilla_user_client.post(
            url,
            data={
                "name": "Test Indicator",
                "name_fr": "Test Indicator FR",
                "category": Indicator.CATEGORY_CHOICES[-1][0],
                "topic": Indicator.TOPIC_CHOICES[-1][0],
                "detailed_indicator": "Test Detailed Indicator",
                "sub_indicator_measurement": "Test Sub Indicator Measurement",
                "sub_indicator_measurement_fr": "Test Sub Indicator Measurement FR",
                "measure_text_fr": "Test Measure Text FR",
                "impact_text_fr": "Test Impact Text FR",
                "title_age_fr": "Test Title Age FR",
                "title_province_territory_fr": "Test Title Province Territory FR",
            },
        )
        assert response.status_code == 302

    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"
    assert indicator.name_fr == "Test Indicator FR"
    assert (
        indicator.sub_indicator_measurement_fr
        == "Test Sub Indicator Measurement FR"
    )
    assert indicator.measure_text_fr == "Test Measure Text FR"
    assert indicator.impact_text_fr == "Test Impact Text FR"
    assert indicator.title_age_fr == "Test Title Age FR"
    assert (
        indicator.title_province_territory_fr
        == "Test Title Province Territory FR"
    )


def test_edit_indicator(vanilla_user_client):
    ind = IndicatorFactory()
    url = reverse("edit_indicator", args=[ind.id])

    with patch_rules(can_access_indicator=True, can_edit_indicator=False):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

    with patch_rules(can_edit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200

    data = {
        "name": "Test Indicator",
        "category": ind.category,
        "topic": ind.topic,
        "detailed_indicator": "Test Detailed Indicator",
        "sub_indicator_measurement": "Test Sub Indicator Measurement",
    }
    with patch_rules(can_edit_indicator=True):
        resp = vanilla_user_client.post(url, data=data)
        assert resp.status_code == 302
        assert resp.url == reverse("view_indicator", args=[ind.id])
