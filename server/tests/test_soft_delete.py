from unittest.mock import patch

from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.constants import SUBMISSION_STATUSES
from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, IndicatorDatum, Period
from cpho.queries import get_submission_statuses

from tests.api.api_test_utils import get_promise_result

from api.dataloaders import SubmittedDatumByIndicatorYearLoader


def test_soft_delete(vanilla_user_client, django_assert_max_num_queries):
    period = Period.objects.get(
        year=2021, year_type=Period.CALENDAR_YEAR_TYPE, quarter=None
    )
    indicator = IndicatorFactory()
    indicator_id = indicator.id
    age_dim_type = DimensionType.objects.get(code="age")
    record0_25 = indicator.data.create(
        period=period,
        dimension_type=age_dim_type,
        literal_dimension_val="0-25",
        value=5,
    )
    record25_50 = indicator.data.create(
        period=period,
        dimension_type=age_dim_type,
        literal_dimension_val="25-50",
        value=6,
    )
    record_51_75 = indicator.data.create(
        period=period,
        dimension_type=age_dim_type,
        literal_dimension_val="51-75",
        value=7,
    )

    # soft-delete the first datum
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 3,
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
        "agegroup-2-literal_dimension_val": "51-75",
        "agegroup-2-is_deleted": "on",
    }
    url = reverse(
        "manage_indicator_data",
        args=[indicator.id, period.id, age_dim_type.pk],
    )

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    # test object manager should show all objects; including deleted ones
    assert (
        IndicatorDatum.objects.filter(
            indicator=indicator, period=period
        ).count()
        == 3
    )
    # test active objects should only show not deleted items
    assert (
        IndicatorDatum.active_objects.filter(
            indicator=indicator, period=period
        ).count()
        == 2
    )

    record_51_75 = IndicatorDatum.objects.filter(
        indicator=indicator,
        period=period,
        literal_dimension_val="51-75",
        dimension_type=age_dim_type,
    ).first()
    # check that the record is soft deleted
    assert record_51_75.is_deleted is True
    assert record_51_75.deletion_time is not None

    # submit all data as program including deleted data
    url = reverse("submit_indicator_data_all", args=[indicator_id, period.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 302

    statuses = get_submission_statuses(indicator, period)

    # submit all data as hso including deleted data
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }

    url = reverse("submit_indicator_data_all", args=[indicator_id, period.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "hso"})
        assert resp.status_code == 302

    statuses = get_submission_statuses(indicator, period)
    record_51_75_latest = (
        IndicatorDatum.objects.filter(
            indicator=indicator,
            period=period,
            literal_dimension_val="51-75",
            dimension_type=age_dim_type,
        )
        .first()
        .versions.last()
    )
    # deleted record should also get submitted
    assert record_51_75_latest.is_deleted is True
    assert record_51_75_latest.is_program_submitted is True
    assert record_51_75_latest.is_hso_submitted is True

    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }

    # query the api to get only non deleted data
    dataloader_instance_cache = {}

    def promise_code():
        data = yield SubmittedDatumByIndicatorYearLoader(
            dataloader_instance_cache
        ).load_many([(indicator.id, 2021)])
        return data

    with django_assert_max_num_queries(2):
        # this dataloader makes 2 queries per batch
        data_all = get_promise_result(promise_code)
        data_2021 = data_all[0]

    assert len(data_2021) == 2

    # soft-delete the last 2 items
    data = {
        "predefined-TOTAL_FORMS": 0,
        "predefined-INITIAL_FORMS": 0,
        "predefined-MIN_NUM_FORMS": 0,
        "predefined-MAX_NUM_FORMS": 1000,
        "agegroup-TOTAL_FORMS": 2,
        "agegroup-INITIAL_FORMS": 2,
        "agegroup-MIN_NUM_FORMS": 0,
        "agegroup-MAX_NUM_FORMS": 1000,
        "agegroup-0-id": record0_25.id,
        "agegroup-0-literal_dimension_val": "0-25",
        "agegroup-0-value": 5.5,
        "agegroup-0-is_deleted": "on",
        "agegroup-1-id": record25_50.id,
        "agegroup-1-literal_dimension_val": "25-50",
        "agegroup-1-value": 7.5,
        "agegroup-1-is_deleted": "on",
    }
    url = reverse(
        "manage_indicator_data",
        args=[indicator.id, period.id, age_dim_type.pk],
    )

    with patch_rules(can_edit_indicator_data=True):
        response = vanilla_user_client.post(url, data=data)
        assert response.status_code == 302

    # All age data is deleted after submission
    # User should not be able to see age data anymore
    # Users will still see status "modified since last submission" to indicated deletion
    statuses = get_submission_statuses(indicator, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "hso_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        "program_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "program_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
    }

    # query the api to get only non deleted data as the deletions are not yet submitted
    dataloader_instance_cache = {}

    with django_assert_max_num_queries(2):
        # this dataloader makes 2 queries per batch
        data_all = get_promise_result(promise_code)
        data_2021 = data_all[0]

    assert len(data_2021) == 2

    # submit the change (deletion of all data) as program
    url = reverse("submit_indicator_data_all", args=[indicator_id, period.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 302

    # after all data is deleted and data is program submitted
    # status should return to no data
    statuses = get_submission_statuses(indicator, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "hso_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        "program_statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }

    url = reverse("submit_indicator_data_all", args=[indicator_id, period.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "hso"})
        assert resp.status_code == 302

    statuses = get_submission_statuses(indicator, period)

    assert statuses == {
        "hso_statuses_by_dimension_type_id": {},
        "hso_global_status": SUBMISSION_STATUSES.NO_DATA,
        "program_statuses_by_dimension_type_id": {},
        "program_global_status": SUBMISSION_STATUSES.NO_DATA,
    }
