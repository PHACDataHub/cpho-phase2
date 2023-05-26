from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import DimensionType, DimensionValue, IndicatorDatum
from django.urls import reverse


def test_create_from_scratch(vanilla_user_client):
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")
    url = reverse("manage_indicator_data", args=[ind.id, sex_cat.pk])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "form-TOTAL_FORMS": 2,
        "form-INITIAL_FORMS": 2,
        "form-MIN_NUM_FORMS": 0,
        "form-MAX_NUM_FORMS": 1000,
        "form-0-value": 5,
        "form-1-value": 6,
    }
    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302

    male_val = sex_cat.possible_values.get(value="m")
    female_val = sex_cat.possible_values.get(value="f")
    assert ind.data.get(dimension_value=male_val).value == 5.0
    assert ind.data.get(dimension_value=female_val).value == 6.0
