from django.urls import reverse

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import Benchmarking, Country

from .utils_for_tests import patch_rules


def test_benchmarking(vanilla_user_client):
    ind = IndicatorFactory()
    ind.save()
    url = reverse("manage_benchmarking_data", args=[ind.id])

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    aus = Country.objects.get(name_en="Australia")
    canada = Country.objects.get(name_en="Canada")

    data = {
        "benchmarking-TOTAL_FORMS": 2,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-value": 1,
        "benchmarking-0-year": 2020,
        # "benchmarking-0-standard_deviation": 0.1,
        "benchmarking-0-comparison_to_oecd_avg": Benchmarking.COMPARISON_CHOICES[
            1
        ][
            0
        ],
        "benchmarking-1-oecd_country": canada.id,
        "benchmarking-1-value": 2,
        "benchmarking-1-year": 2020,
        # "benchmarking-1-standard_deviation": 0.2,
        "benchmarking-1-comparison_to_oecd_avg": Benchmarking.COMPARISON_CHOICES[
            1
        ][
            0
        ],
    }

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    created_data = Benchmarking.active_objects.filter(indicator=ind)
    assert created_data.count() == 2
    aus_data = created_data.get(oecd_country=aus)
    assert aus_data.value == 1
    assert aus_data.year == 2020
    # assert aus_data.standard_deviation == 0.1
    canada_data = created_data.get(oecd_country=canada)
    assert canada_data.value == 2
    assert canada_data.year == 2020
    # assert canada_data.standard_deviation == 0.2

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    data = {
        "benchmarking-TOTAL_FORMS": 2,
        "benchmarking-INITIAL_FORMS": 2,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-id": aus_data.id,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-value": 1.1,  # change value
        "benchmarking-0-year": 2020,
        # "benchmarking-0-standard_deviation": 0.1,
        "benchmarking-0-comparison_to_oecd_avg": Benchmarking.COMPARISON_CHOICES[
            1
        ][
            0
        ],
        "benchmarking-1-id": canada_data.id,
        "benchmarking-1-oecd_country": canada.id,
        "benchmarking-1-value": 2,
        "benchmarking-1-year": 2020,
        # "benchmarking-1-standard_deviation": 0.2,
        "benchmarking-1-comparison_to_oecd_avg": Benchmarking.COMPARISON_CHOICES[
            1
        ][
            0
        ],
        "benchmarking-1-is_deleted": "on",  # delete canada
    }

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    created_data = Benchmarking.active_objects.filter(indicator=ind)

    assert created_data.count() == 1
    aus_data = created_data.get(oecd_country=aus)
    assert aus_data.value == 1.1

    deleted_data = Benchmarking.objects.filter(indicator=ind)
    assert deleted_data.count() == 2
    canada_data = deleted_data.get(oecd_country=canada)
    assert canada_data.is_deleted == True
    assert canada_data.deletion_time is not None
