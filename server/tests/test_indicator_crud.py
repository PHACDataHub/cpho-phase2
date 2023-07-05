from django.urls import reverse

from cpho.model_factories import IndicatorFactory
from cpho.models import Indicator


def test_create_indicator(vanilla_user_client):
    url = reverse("create_indicator")
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    response = vanilla_user_client.post(
        url,
        data={
            "name": "Test Indicator",
            "category": Indicator.CATEGORY_CHOICES[-1][0],
            "sub_category": Indicator.SUB_CATEGORY_CHOICES[-1][0],
            "detailed_indicator": "Test Detailed Indicator",
            "sub_indicator_measurement": "Test Sub Indicator Measurement",
        },
    )
    assert response.status_code == 302

    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"
