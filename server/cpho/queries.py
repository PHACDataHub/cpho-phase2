from collections import defaultdict

from cpho.constants import SUBMISSION_STATUSES
from cpho.models import DimensionType, DimensionValue
from cpho.util import group_by

from .models import IndicatorDirectoryUserAccess


def is_submission_out_of_date(indicator_datum):
    return


def aggregate_statuses(statuses):
    if len(statuses) < 1:
        return SUBMISSION_STATUSES.NO_DATA

    if all(status == SUBMISSION_STATUSES.SUBMITTED for status in statuses):
        return SUBMISSION_STATUSES.SUBMITTED
    elif all(
        status
        in (
            SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            SUBMISSION_STATUSES.SUBMITTED,
        )
        for status in statuses
    ):
        return SUBMISSION_STATUSES.PROGRAM_SUBMITTED
    elif any(status == SUBMISSION_STATUSES.NO_DATA for status in statuses):
        return SUBMISSION_STATUSES.NO_DATA
    elif any(
        status == SUBMISSION_STATUSES.NOT_YET_SUBMITTED for status in statuses
    ):
        return SUBMISSION_STATUSES.NOT_YET_SUBMITTED
    elif any(
        status == SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
        for status in statuses
    ):
        return SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION

    else:
        raise Exception("Shouldn't get here...")


def get_submission_statuses(indicator, period):
    data = (
        indicator.data.filter(period=period)
        .with_submission_annotations()
        .prefetch_related("dimension_value", "dimension_type")
    )
    dimension_types = set([d.dimension_type for d in data])
    # dimension_values = [d.dimension_value for d in data]
    # data_by_dimension_value_id = {d.dimension_value_id: d for d in data}
    data_by_dimension_type_id = group_by(data, lambda d: d.dimension_type_id)

    submission_status_by_dimension_type_id = defaultdict(
        lambda: SUBMISSION_STATUSES.NO_DATA
    )

    for dimension_type in dimension_types:
        dim_id = dimension_type.id
        data_for_dim = data_by_dimension_type_id[dim_id]
        if not data_for_dim:
            submission_status_by_dimension_type_id[
                dim_id
            ] = SUBMISSION_STATUSES.NO_DATA
            continue

        submission_statuses = [
            datum.submission_status for datum in data_for_dim
        ]
        if dimension_type.is_literal:
            all_deleted = all(d.is_deleted for d in data_for_dim)
            if (
                all_deleted
                and aggregate_statuses(submission_statuses)
                != SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
            ):
                if submission_status_by_dimension_type_id[dim_id]:
                    submission_status_by_dimension_type_id.pop(dim_id)
                    continue

        submission_status_by_dimension_type_id[dim_id] = aggregate_statuses(
            submission_statuses
        )

    global_status = aggregate_statuses(
        list(submission_status_by_dimension_type_id.values())
    )

    return {
        "statuses_by_dimension_type_id": submission_status_by_dimension_type_id,
        "global_status": global_status,
    }


def relevant_dimension_types_for_period(indicator, period):
    data = (
        indicator.data.filter(period=period)
        .prefetch_related("dimension_type")
        .distinct("dimension_type")
    )
    dimension_types = {d.dimension_type for d in data}.union(
        indicator.relevant_dimensions.all()
    )
    return list(dimension_types)


def get_indicators_for_user(user_id):
    directory_access_links = IndicatorDirectoryUserAccess.objects.filter(
        user_id=user_id
    ).prefetch_related("directory__indicators")
    all_indicators = set()
    for link in directory_access_links:
        indicators = set(link.directory.indicators.all())
        all_indicators.update(indicators)

    return all_indicators


def get_indicator_directories_for_user(user_id):
    directory_access_links = IndicatorDirectoryUserAccess.objects.filter(
        user_id=user_id
    ).prefetch_related("directory")
    return [link.directory for link in directory_access_links]
