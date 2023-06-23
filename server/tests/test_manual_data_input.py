from django.urls import reverse

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import DimensionType, DimensionValue, IndicatorDatum


def test_predefined_create_from_scratch(vanilla_user_client):
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")
    url = reverse("manage_indicator_data", args=[ind.id, sex_cat.pk])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "agegroup-TOTAL_FORMS": 0,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "predefined-TOTAL_FORMS": 2,
        "predefined-INITIAL_FORMS": 2,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "predefined-0-value": 5,
        "predefined-1-value": 6,
    }
    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302

    male_val = sex_cat.possible_values.get(value="m")
    female_val = sex_cat.possible_values.get(value="f")
    assert ind.data.get(dimension_value=male_val).value == 5.0
    assert ind.data.get(dimension_value=female_val).value == 6.0


def test_predefined_existing_data(vanilla_user_client):
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")

    male_record = ind.data.create(
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="m"),
        value=1.0,
    )

    url = reverse("manage_indicator_data", args=[ind.id, sex_cat.pk])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "predefined-TOTAL_FORMS": 2,
        "predefined-INITIAL_FORMS": 2,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 0,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "predefined-0-value": 1.1,
        "predefined-1-value": 2.0,
    }
    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302

    male_val = sex_cat.possible_values.get(value="m")
    female_val = sex_cat.possible_values.get(value="f")
    assert ind.data.get(dimension_value=male_val) == male_record
    male_record.refresh_from_db()
    assert male_record.value == 1.1
    assert ind.data.get(dimension_value=female_val).value == 2.0


def test_create_agegroups_from_scratch(vanilla_user_client):
    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")
    url = reverse("manage_indicator_data", args=[ind.id, age_cat.pk])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-50",
        "agegroup-0-value": 5,
        "agegroup-1-literal_dimension_val": "50-120",
        "agegroup-1-value": 7.5,
    }

    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302

    created_data = IndicatorDatum.objects.filter(
        dimension_type=age_cat, indicator=ind
    )
    assert created_data.count() == 2
    assert created_data.get(literal_dimension_val="0-50").value == 5.0
    assert created_data.get(literal_dimension_val="50-120").value == 7.5


def test_agegroups_existing_data(vanilla_user_client):
    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")

    record0_25 = ind.data.create(
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    record25_50 = ind.data.create(
        dimension_type=age_cat,
        literal_dimension_val="25-50",
        value=6,
    )
    record_51_75 = ind.data.create(
        dimension_type=age_cat,
        literal_dimension_val="51-75",
        value=7,
    )

    url = reverse("manage_indicator_data", args=[ind.id, age_cat.pk])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 5,
        "agegroup-INITIAL_FORMS": 3,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-id": record0_25.id,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.5,
        "agegroup-1-id": record25_50.id,
        "agegroup-1-literal_dimension_val": "25-50",
        "agegroup-1-value": 7.5,
        # delete record_51_75
        "agegroup-2-id": record_51_75.id,
        "agegroup-2-DELETE": "on",
        "agegroup-3-literal_dimension_val": "50-120",
        "agegroup-3-value": 10.5,
        # also add an extra record that is immediately deleted
        # just to show nothing happens
        "agegroup-4-literal_dimension_val": "120-150",
        "agegroup-4-DELETE": "on",
    }
    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302
    ind.refresh_from_db()
    assert ind.data.count() == 3
    assert ind.data.get(literal_dimension_val="0-25") == record0_25
    assert ind.data.get(literal_dimension_val="25-50") == record25_50
    record0_25.refresh_from_db()
    record25_50.refresh_from_db()
    assert record0_25.value == 5.5
    assert record25_50.value == 7.5
    assert ind.data.get(literal_dimension_val="50-120").value == 10.5

    # assert deleted
    assert not IndicatorDatum.objects.filter(id=record_51_75.id).exists()


def test_modify_all_dimensions(vanilla_user_client):
    # delete other dimensions to make POST more manageable
    DimensionValue.objects.exclude(
        dimension_type__code__in=["age", "sex"]
    ).delete()
    DimensionType.objects.exclude(code__in=["age", "sex"]).delete()

    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")
    sex_cat = DimensionType.objects.get(code="sex")

    male_dimension_value = sex_cat.possible_values.get(value="m")

    # one existing record in both dimensions
    record0_25 = ind.data.create(
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    male_record = ind.data.create(
        dimension_type=sex_cat, dimension_value=male_dimension_value, value=6
    )

    url = reverse("manage_indicator_data_all", args=[ind.id])
    response = vanilla_user_client.get(url)
    assert response.status_code == 200

    data = {
        "predefined-TOTAL_FORMS": 2,
        "predefined-INITIAL_FORMS": 2,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "predefined-0-value": 1.1,
        "predefined-1-value": 2.0,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 1,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-id": record0_25.id,
        "agegroup-0-literal_dimension_val": "1-25",
        "agegroup-0-value": 5.5,
        "agegroup-1-literal_dimension_val": "25-50",
        "agegroup-1-value": 7.5,
    }
    response = vanilla_user_client.post(url, data=data)
    assert response.status_code == 302

    ind.refresh_from_db()
    assert ind.data.count() == 4

    assert (
        ind.data.get(
            dimension_type=sex_cat, dimension_value=male_dimension_value
        )
        == male_record
    )
    assert (
        ind.data.get(
            dimension_type=sex_cat, dimension_value=male_dimension_value
        ).value
        == 1.1
    )
    assert (
        ind.data.get(dimension_type=sex_cat, dimension_value__value="f").value
        == 2.0
    )

    assert (
        ind.data.get(dimension_type=age_cat, literal_dimension_val="1-25")
        == record0_25
    )
    assert (
        ind.data.get(
            dimension_type=age_cat, literal_dimension_val="25-50"
        ).value
        == 7.5
    )
