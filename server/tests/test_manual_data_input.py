from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import DimensionType, DimensionValue, IndicatorDatum, Period
from cpho.views import IndicatorDatumForm, ReadOnlyIndicatorDatumForm


def test_predefined_create_from_scratch(vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")
    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, sex_cat.pk]
    )
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

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

    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 403

    male_val = sex_cat.possible_values.get(value="m")
    female_val = sex_cat.possible_values.get(value="f")
    assert ind.data.get(dimension_value=male_val).value == 5.0
    assert ind.data.get(dimension_value=female_val).value == 6.0
    assert set(ind.data.all()) == set(ind.data.filter(period=period))


def test_predefined_existing_data(vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")

    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="m"),
        value=1.0,
    )

    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, sex_cat.pk]
    )
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

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
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 403

    male_val = sex_cat.possible_values.get(value="m")
    female_val = sex_cat.possible_values.get(value="f")
    assert ind.data.get(dimension_value=male_val) == male_record
    male_record.refresh_from_db()
    assert male_record.value == 1.1
    assert ind.data.get(dimension_value=female_val).value == 2.0


def test_create_agegroups_from_scratch(vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")
    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, age_cat.pk]
    )
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

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

    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 403

    created_data = IndicatorDatum.active_objects.filter(
        dimension_type=age_cat, indicator=ind, period=period
    )
    assert created_data.count() == 2
    assert created_data.get(literal_dimension_val="0-50").value == 5.0
    assert created_data.get(literal_dimension_val="50-120").value == 7.5


def test_agegroups_existing_data(vanilla_user_client):
    period = Period.objects.first()

    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")

    record0_25 = ind.data.create(
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    record25_50 = ind.data.create(
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="25-50",
        value=6,
    )
    record_51_75 = ind.data.create(
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="51-75",
        value=7,
    )

    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, age_cat.pk]
    )
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 6,
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
        "agegroup-2-is_deleted": "on",
        "agegroup-3-literal_dimension_val": "50-120",
        "agegroup-3-value": 10.5,
        # also add an extra record that is immediately deleted
        # just to show nothing happens
        "agegroup-4-literal_dimension_val": "120-150",
        "agegroup-4-is_deleted": "on",
        # add a new record too, it shouldn't matter that it comes after 4?
        "agegroup-5-literal_dimension_val": "75-120",
        "agegroup-5-value": 20.1,
    }
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 403
    ind.refresh_from_db()
    assert ind.data.filter(period=period, is_deleted=False).count() == 4
    deleted_record = ind.data.filter(
        period=period, literal_dimension_val="51-75"
    )
    assert deleted_record.count() == 1
    assert deleted_record.first().is_deleted
    assert deleted_record.first().deletion_time is not None
    assert ind.data.get(literal_dimension_val="0-25") == record0_25
    assert ind.data.get(literal_dimension_val="25-50") == record25_50
    record0_25.refresh_from_db()
    record25_50.refresh_from_db()
    assert record0_25.value == 5.5
    assert record25_50.value == 7.5
    assert ind.data.get(literal_dimension_val="50-120").value == 10.5

    # assert deleted
    assert not IndicatorDatum.active_objects.filter(
        id=record_51_75.id
    ).exists()

    new_record = ind.data.get(literal_dimension_val="75-120")
    assert new_record.value == 20.1


def test_modify_all_dimensions(vanilla_user_client):
    period = Period.objects.first()
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
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=male_dimension_value,
        value=6,
    )

    url = reverse("manage_indicator_data_all", args=[ind.id, period.id])
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

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
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=False
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 403

    ind.refresh_from_db()
    assert ind.data.filter(is_deleted=False).count() == 4

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

    # check periods correctly assigned on all records
    assert not ind.data.exclude(period=period)


def test_non_changes_dont_create_versions(vanilla_user_client):
    period = Period.objects.first()
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
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=male_dimension_value,
        value=6,
    )

    url = reverse("manage_indicator_data_all", args=[ind.id, period.id])

    data = {
        "predefined-TOTAL_FORMS": 2,
        "predefined-INITIAL_FORMS": 2,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "predefined-0-value": 6,  # male record
        "predefined-1-value": 2.0,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 1,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-id": record0_25.id,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5,
        # add new datum:
        "agegroup-1-literal_dimension_val": "25-50",
        "agegroup-1-value": 7.5,
    }
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)

    assert male_record.versions.count() == 1
    assert record0_25.versions.count() == 1


def test_readonly_indicator_data(vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")

    record0_25 = ind.data.create(
        period=period,
        dimension_type=age_cat,
        literal_dimension_val="0-25",
        value=5,
    )
    sex_cat = DimensionType.objects.get(code="sex")

    male_dimension_value = sex_cat.possible_values.get(value="m")

    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=male_dimension_value,
        value=6,
    )

    url = reverse("manage_indicator_data_all", args=[ind.id, period.id])
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
        formset = response.context["age_group_formset"]
        for form in formset:
            assert isinstance(form, ReadOnlyIndicatorDatumForm)
        formset = response.context["predefined_values_formset"]
        for form in formset:
            assert isinstance(form, ReadOnlyIndicatorDatumForm)

    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
        formset = response.context["age_group_formset"]
        for form in formset:
            assert isinstance(form, IndicatorDatumForm)
        formset = response.context["predefined_values_formset"]
        for form in formset:
            assert isinstance(form, IndicatorDatumForm)


def test_indicator_data_form_validation(vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    age_cat = DimensionType.objects.get(code="age")
    url = reverse(
        "manage_indicator_data", args=[ind.id, period.id, age_cat.pk]
    )
    # only delete set to true
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-is_deleted": "on",
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        # no context if form is valid
        assert response.context is None

    # test with negative value
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": -5.0,
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # check with inconsistent upper ci
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-0-value_upper_bound": 4.0,
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # check with inconsistent lower ci
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-0-value_lower_bound": 6.0,
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # check with inconsistent single year timeframe
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-0-single_year_timeframe": "hello",
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # check with inconsistent multiple year timeframe
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 1,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-0-multi_year_timeframe": "2020",
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # Dupe: check literal dimension value cannot be the same (unique together check)
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-1-literal_dimension_val": "0-25",
        "agegroup-1-value": 6.0,
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        assert response.context["age_group_formset"].errors is not None

    # Dupe with one delete
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 0,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.0,
        "agegroup-1-literal_dimension_val": "0-25",
        "agegroup-1-value": 6.0,
        "agegroup-1-is_deleted": "on",
    }
    with patch_rules(
        can_edit_indicator_data=False, can_view_indicator_data=True
    ):
        response = vanilla_user_client.post(url, data=data)
        # no context if form is valid
        assert response.context is None
