from django.db import transaction

from cpho.constants import SUBMISSION_TYPES
from cpho.models import IndicatorDataSubmission, IndicatorDatumHistory


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
