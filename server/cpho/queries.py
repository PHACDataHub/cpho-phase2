from collections import defaultdict

from cpho.constants import SUBMISSION_STATUSES
from cpho.models import DimensionType, DimensionValue, Indicator
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
        status == SUBMISSION_STATUSES.PROGRAM_SUBMITTED for status in statuses
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

    elif (
        SUBMISSION_STATUSES.PROGRAM_SUBMITTED in statuses
        and SUBMISSION_STATUSES.SUBMITTED in statuses
    ):
        raise TypeError(
            "Program submitted and HSO submitted statuses should not be mixed."
        )

    else:
        raise Exception("Shouldn't get here...")


def get_metadata_submission_statuses(indicator):
    benchmarking_qs = (
        indicator.benchmarking.all().with_submission_annotations()
    )
    trend_analysis_qs = (
        indicator.trend_analysis.all().with_submission_annotations()
    )
    indicator_qs = Indicator.objects.filter(
        id=indicator.id
    ).with_submission_annotations()

    hso_submission_status_benchmarking = aggregate_statuses(
        [d.submission_status(submission_type="hso") for d in benchmarking_qs]
    )
    program_submission_status_benchmarking = aggregate_statuses(
        [
            d.submission_status(submission_type="program")
            for d in benchmarking_qs
        ]
    )

    hso_submission_status_trend = aggregate_statuses(
        [d.submission_status(submission_type="hso") for d in trend_analysis_qs]
    )
    program_submission_status_trend = aggregate_statuses(
        [
            d.submission_status(submission_type="program")
            for d in trend_analysis_qs
        ]
    )

    hso_all_statuses = []
    program_all_statuses = []

    if hso_submission_status_benchmarking != SUBMISSION_STATUSES.NO_DATA:
        hso_all_statuses.append(hso_submission_status_benchmarking)
    if hso_submission_status_trend != SUBMISSION_STATUSES.NO_DATA:
        hso_all_statuses.append(hso_submission_status_trend)
    indicator_hso_submission_status = indicator_qs[0].submission_status(
        submission_type="hso"
    )
    if indicator_hso_submission_status != SUBMISSION_STATUSES.NO_DATA:
        hso_all_statuses.append(indicator_hso_submission_status)

    if program_submission_status_benchmarking != SUBMISSION_STATUSES.NO_DATA:
        program_all_statuses.append(program_submission_status_benchmarking)
    if program_submission_status_trend != SUBMISSION_STATUSES.NO_DATA:
        program_all_statuses.append(program_submission_status_trend)
    indicator_program_submission_status = indicator_qs[0].submission_status(
        submission_type="program"
    )
    if indicator_program_submission_status != SUBMISSION_STATUSES.NO_DATA:
        program_all_statuses.append(indicator_program_submission_status)

    hso_global_status = aggregate_statuses(hso_all_statuses)
    program_global_status = aggregate_statuses(program_all_statuses)

    return {
        "hso_global_status": hso_global_status,
        "hso_benchmarking_status": hso_submission_status_benchmarking,
        "hso_trend_status": hso_submission_status_trend,
        "hso_indicator_status": indicator_hso_submission_status,
        "program_global_status": program_global_status,
        "program_benchmarking_status": program_submission_status_benchmarking,
        "program_trend_status": program_submission_status_trend,
        "program_indicator_status": indicator_program_submission_status,
    }


def get_submission_statuses(indicator, period):
    data = (
        indicator.data.filter(period=period)
        .with_submission_annotations()
        .prefetch_related("dimension_value", "dimension_type")
    )
    dimension_types = set([d.dimension_type for d in data])
    data_by_dimension_type_id = group_by(data, lambda d: d.dimension_type_id)

    hso_submission_status_by_dimension_type_id = defaultdict(
        lambda: SUBMISSION_STATUSES.NO_DATA
    )
    program_submission_status_by_dimension_type_id = defaultdict(
        lambda: SUBMISSION_STATUSES.NO_DATA
    )

    for dimension_type in dimension_types:
        dim_id = dimension_type.id
        data_for_dim = data_by_dimension_type_id[dim_id]
        if not data_for_dim:
            hso_submission_status_by_dimension_type_id[dim_id] = (
                SUBMISSION_STATUSES.NO_DATA
            )
            program_submission_status_by_dimension_type_id[dim_id] = (
                SUBMISSION_STATUSES.NO_DATA
            )
            continue

        hso_submission_statuses = [
            datum.submission_status(submission_type="hso")
            for datum in data_for_dim
        ]
        program_submission_statuses = [
            datum.submission_status(submission_type="program")
            for datum in data_for_dim
        ]

        hso_submission_status_by_dimension_type_id[dim_id] = (
            aggregate_statuses(hso_submission_statuses)
        )
        program_submission_status_by_dimension_type_id[dim_id] = (
            aggregate_statuses(program_submission_statuses)
        )
        if dimension_type.is_literal:
            all_deleted = all(d.is_deleted for d in data_for_dim)
            if all_deleted:
                if (
                    hso_submission_status_by_dimension_type_id[dim_id]
                    != SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
                    and program_submission_status_by_dimension_type_id[dim_id]
                    != SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
                ):
                    program_submission_status_by_dimension_type_id.pop(dim_id)
                    hso_submission_status_by_dimension_type_id.pop(dim_id)
                continue

    hso_global_status = aggregate_statuses(
        list(hso_submission_status_by_dimension_type_id.values())
    )
    program_global_status = aggregate_statuses(
        list(program_submission_status_by_dimension_type_id.values())
    )

    return {
        "hso_statuses_by_dimension_type_id": hso_submission_status_by_dimension_type_id,
        "program_statuses_by_dimension_type_id": program_submission_status_by_dimension_type_id,
        "hso_global_status": hso_global_status,
        "program_global_status": program_global_status,
    }


def relevant_dimension_types_for_period(indicator, period):
    ids_of_dimensions_with_data = (
        indicator.data.filter(period=period)
        .values("dimension_type_id")
        .distinct()
    )
    dimensions_with_data = DimensionType.objects.filter(
        id__in=ids_of_dimensions_with_data
    )
    dimension_types = set(dimensions_with_data).union(
        indicator.relevant_dimensions.all()
    )
    dimension_types = sorted(dimension_types, key=lambda d: d.order)
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
