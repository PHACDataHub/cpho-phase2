from collections import defaultdict

from cpho.constants import APPROVAL_STATUSES
from cpho.models import DimensionType, DimensionValue
from cpho.util import group_by


def is_submission_out_of_date(indicator_datum):
    return


def aggregate_statuses(statuses):
    if len(statuses) < 1:
        return APPROVAL_STATUSES.NO_DATA

    if all(status == APPROVAL_STATUSES.SUBMITTED for status in statuses):
        return APPROVAL_STATUSES.SUBMITTED
    elif all(
        status
        in (APPROVAL_STATUSES.PROGRAM_SUBMITTED, APPROVAL_STATUSES.SUBMITTED)
        for status in statuses
    ):
        return APPROVAL_STATUSES.PROGRAM_SUBMITTED
    elif any(status == APPROVAL_STATUSES.NO_DATA for status in statuses):
        return APPROVAL_STATUSES.NO_DATA
    elif any(
        status == APPROVAL_STATUSES.NOT_YET_SUBMITTED for status in statuses
    ):
        return APPROVAL_STATUSES.NOT_YET_SUBMITTED
    elif any(
        status == APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
        for status in statuses
    ):
        return APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION

    else:
        raise Exception("Shouldn't get here...")


def get_approval_statuses(indicator, period):
    data = (
        indicator.data.filter(period=period)
        .with_approval_annotations()
        .prefetch_related("dimension_value", "dimension_type")
    )

    dimension_types = [d.dimension_type for d in data]
    # dimension_values = [d.dimension_value for d in data]
    # data_by_dimension_value_id = {d.dimension_value_id: d for d in data}
    data_by_dimension_type_id = group_by(data, lambda d: d.dimension_type_id)

    approval_status_by_dimension_type_id = defaultdict(
        lambda: APPROVAL_STATUSES.NO_DATA
    )

    for dimension_type in dimension_types:
        dim_id = dimension_type.id
        if not data_by_dimension_type_id[dim_id]:
            approval_status_by_dimension_type_id[
                dim_id
            ] = APPROVAL_STATUSES.NO_DATA
            continue

        data_for_dim = data_by_dimension_type_id[dim_id]
        approval_statuses = [datum.submission_status for datum in data_for_dim]

        approval_status_by_dimension_type_id[dim_id] = aggregate_statuses(
            approval_statuses
        )

    global_status = aggregate_statuses(
        list(approval_status_by_dimension_type_id.values())
    )

    return {
        "statuses_by_dimension_type_id": approval_status_by_dimension_type_id,
        "global_status": global_status,
    }
