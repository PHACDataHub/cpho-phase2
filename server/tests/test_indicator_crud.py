from django.urls import reverse

from cpho.model_factories import IndicatorFactory
from cpho.models import Indicator

from .utils_for_tests import patch_rules


def test_create_indicator(vanilla_user_client):
    url = reverse("create_indicator")
    with patch_rules(can_create_indicator=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

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
        assert response.status_code == 302

    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"


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
