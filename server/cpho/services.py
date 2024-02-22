from django.db import transaction

from cpho.constants import SUBMISSION_TYPES
from cpho.models import (
    BenchmarkingHistory,
    Indicator,
    IndicatorDataSubmission,
    IndicatorDatumHistory,
    IndicatorHistory,
    IndicatorMetaDataSubmission,
    TrendAnalysisHistory,
)


class SubmitIndicatorDataService:
    def __init__(
        self, indicator, period, dimension_type, submission_type, user
    ):
        self.indicator = indicator
        self.period = period
        self.dimension_type = dimension_type
        assert (
            submission_type in SUBMISSION_TYPES
        ), f"submission type must be in {SUBMISSION_TYPES}"
        self.submission_type = submission_type
        self.user = user

    @transaction.atomic
    def perform(self):
        version_ids_to_submit = self._get_version_ids_to_submit()

        version_qs = IndicatorDatumHistory.objects.filter(
            id__in=version_ids_to_submit
        )

        if self.submission_type == "hso":
            version_qs.update(is_hso_submitted=True)
        elif self.submission_type == "program":
            version_qs.update(is_program_submitted=True)

        IndicatorDataSubmission.objects.create(
            submitted_by=self.user,
            indicator=self.indicator,
            period=self.period,
            dimension_type=self.dimension_type,
            submission_type=self.submission_type,
        )

    def _get_version_ids_to_submit(self):
        qs = self.indicator.data.filter(
            period=self.period
        ).with_last_version_id()

        if self.dimension_type:
            qs = qs.filter(dimension_type=self.dimension_type)

        most_recent_version_ids = [d.last_version_id for d in qs]
        return most_recent_version_ids


class SubmitIndicatorMetaDataService:
    def __init__(self, indicator, submission_type, user):
        self.indicator = indicator
        assert (
            submission_type in SUBMISSION_TYPES
        ), f"submission type must be in {SUBMISSION_TYPES}"
        self.submission_type = submission_type
        self.user = user

    @transaction.atomic
    def perform(self):
        version_ids_to_submit = self._get_version_ids_to_submit()

        indicator_qs = IndicatorHistory.objects.filter(
            id=version_ids_to_submit["indicator"]
        )
        benchmarking_qs = BenchmarkingHistory.objects.filter(
            id__in=version_ids_to_submit["benchmarking"]
        )
        trend_qs = TrendAnalysisHistory.objects.filter(
            id__in=version_ids_to_submit["trend"]
        )

        if self.submission_type == "hso":
            indicator_qs.update(is_hso_submitted=True)
            benchmarking_qs.update(is_hso_submitted=True)
            trend_qs.update(is_hso_submitted=True)
        elif self.submission_type == "program":
            indicator_qs.update(is_program_submitted=True)
            benchmarking_qs.update(is_program_submitted=True)
            trend_qs.update(is_program_submitted=True)

        IndicatorMetaDataSubmission.objects.create(
            submitted_by=self.user,
            indicator=self.indicator,
            submission_type=self.submission_type,
        )

    def _get_version_ids_to_submit(self):
        indicator_qs = Indicator.objects.filter(
            id=self.indicator.id
        ).with_last_version_id()
        benchmarking_qs = self.indicator.benchmarking.with_last_version_id()
        trend_qs = self.indicator.trend_analysis.with_last_version_id()

        most_recent_version_ids = {
            "indicator": indicator_qs[0].last_version_id,
            "benchmarking": [d.last_version_id for d in benchmarking_qs],
            "trend": [d.last_version_id for d in trend_qs],
        }

        return most_recent_version_ids
