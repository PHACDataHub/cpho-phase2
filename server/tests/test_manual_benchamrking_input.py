from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import Benchmarking, Country


def test_benchmarking(vanilla_user_client):
    ind = IndicatorFactory()
    ind.save()
    url = reverse("manage_benchmarking_data", args=[ind.id])

    with patch_rules(can_access_indicator=True, can_edit_benchmarking=False):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
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
        "benchmarking-0-methodology_differences": "on",
        "benchmarking-1-oecd_country": canada.id,
        "benchmarking-1-value": 2,
        "benchmarking-1-year": 2020,
        # "benchmarking-1-standard_deviation": 0.2,
        "benchmarking-1-comparison_to_oecd_avg": Benchmarking.COMPARISON_CHOICES[
            1
        ][
            0
        ],
        "benchmarking-1-methodology_differences": "",
    }

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    created_data = Benchmarking.active_objects.filter(indicator=ind)
    assert created_data.count() == 2
    aus_data = created_data.get(oecd_country=aus)
    assert aus_data.value == 1
    assert aus_data.year == "2020"
    assert aus_data.methodology_differences == True
    # assert aus_data.standard_deviation == 0.1
    canada_data = created_data.get(oecd_country=canada)
    assert canada_data.value == 2
    assert canada_data.year == "2020"
    assert canada_data.methodology_differences == False
    # assert canada_data.standard_deviation == 0.2

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
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
        "benchmarking-0-methodology_differences": "on",
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

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    created_data = Benchmarking.active_objects.filter(indicator=ind)

    assert created_data.count() == 1
    aus_data = created_data.get(oecd_country=aus)
    assert aus_data.value == 1.1

    all_data = Benchmarking.objects.filter(indicator=ind)
    assert all_data.count() == 2
    canada_data = all_data.get(oecd_country=canada)
    assert canada_data.is_deleted == True
    assert canada_data.deletion_time is not None


def test_benchmarking_form_validation(vanilla_user_client):
    aus = Country.objects.get(name_en="Australia")
    oecd = Country.objects.get(name_en="OECD")
    ind = IndicatorFactory()
    ind.save()
    comparison_better = Benchmarking.COMPARISON_CHOICES[1][0]
    label_anxiety = Benchmarking.LABEL_CHOICES[1][0]
    url = reverse("manage_benchmarking_data", args=[ind.id])
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    # only delete set to true
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-is_deleted": "on",
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        # no context if form is valid
        assert response.context is None

    # submit with just value
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-value": 1,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # check no year required for oecd
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": oecd.id,
        "benchmarking-0-value": 1,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        # no context if form is valid
        assert response.context is None

    # check year required if country not oecd
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-value": 1,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # check value required
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-year": 2020,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # check comparison required
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-year": 2020,
        "benchmarking-0-value": 1,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # check year format
    data = {
        "benchmarking-TOTAL_FORMS": 1,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-year": 20,
        "benchmarking-0-value": 1,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # Dupe: check country and label cannot be the same (unique together check)
    data = {
        "benchmarking-TOTAL_FORMS": 2,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-year": 2020,
        "benchmarking-0-value": 1,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
        "benchmarking-0-labels": label_anxiety,
        "benchmarking-1-oecd_country": aus.id,
        "benchmarking-1-year": 2020,
        "benchmarking-1-value": 1,
        "benchmarking-1-comparison_to_oecd_avg": comparison_better,
        "benchmarking-1-labels": label_anxiety,
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["benchmarking_formset"].errors is not None

    # Dupe with one delete
    data = {
        "benchmarking-TOTAL_FORMS": 2,
        "benchmarking-INITIAL_FORMS": 0,
        "benchmarking-MIN_NUM_FORMS": 0,
        "benchmarking-MAX_NUM_FORMS": 1000,
        "benchmarking-0-oecd_country": aus.id,
        "benchmarking-0-year": 2020,
        "benchmarking-0-value": 1,
        "benchmarking-0-comparison_to_oecd_avg": comparison_better,
        "benchmarking-0-labels": label_anxiety,
        "benchmarking-1-oecd_country": aus.id,
        "benchmarking-1-year": 2020,
        "benchmarking-1-value": 1,
        "benchmarking-1-comparison_to_oecd_avg": comparison_better,
        "benchmarking-1-labels": label_anxiety,
        "benchmarking-1-is_deleted": "on",
    }
    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.post(url, data=data)
        # no context if form is valid
        assert response.context is None
