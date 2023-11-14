from unittest.mock import patch

from django.urls import reverse

from cpho.constants import SUBMISSION_STATUSES
from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatumHistory,
    IndicatorHistory,
    Period,
)
from cpho.queries import get_submission_statuses

from .utils_for_tests import patch_rules


def test_soft_delete(vanilla_user_client):
    period = Period.objects.last()
    indicator = IndicatorFactory()
    indicator_id = indicator.id
    age_dim_type = DimensionType.objects.get(code="age")
    datum1 = IndicatorDatumFactory(
        indicator=indicator,
        literal_dimension_val="datum1",
        period=period,
        dimension_type=age_dim_type,
    )
    datum1.save()
    datum2 = IndicatorDatumFactory(
        indicator=indicator,
        literal_dimension_val="datum2",
        period=period,
        dimension_type=age_dim_type,
    )
    datum2.save()
    datum3 = IndicatorDatumFactory(
        indicator=indicator,
        literal_dimension_val="datum3",
        period=period,
        dimension_type=age_dim_type,
    )
    datum3.save()

    url = reverse("submit_indicator_data_all", args=[indicator_id, period.id])
    with patch_rules(can_submit_as_hso_or_program=True):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 302

    statuses = get_submission_statuses(indicator, period)

    assert statuses == {
        "statuses_by_dimension_type_id": {
            age_dim_type.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }

    # soft-delete the first datum
