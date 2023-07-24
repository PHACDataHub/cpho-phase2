from django.db import transaction

from cpho.constants import APPROVAL_TYPES
from cpho.models import IndicatorDataSubmission, IndicatorDatumHistory


class SubmitIndicatorDataService:
    def __init__(self, indicator, period, dimension_type, approval_type, user):
        self.indicator = indicator
        self.period = period
        self.dimension_type = dimension_type
        assert (
            approval_type in APPROVAL_TYPES
        ), f"approval type must be in {APPROVAL_TYPES}"
        self.approval_type = approval_type
        self.user = user

    @transaction.atomic
    def perform(self):
        version_ids_to_approve = self._get_version_ids_to_approve()

        version_qs = IndicatorDatumHistory.objects.filter(
            id__in=version_ids_to_approve
        )

        if self.approval_type == "hso":
            version_qs.update(is_hso_approved=True)
        elif self.approval_type == "program":
            version_qs.update(is_program_approved=True)

        IndicatorDataSubmission.objects.create(
            submitted_by=self.user,
            indicator=self.indicator,
            period=self.period,
            dimension_type=self.dimension_type,
            approval_type=self.approval_type,
        )

    def _get_version_ids_to_approve(self):
        qs = self.indicator.data.filter(
            period=self.period
        ).with_last_version_id()

        if self.dimension_type:
            qs = qs.filter(dimension_type=self.dimension_type)

        most_recent_version_ids = [d.last_version_id for d in qs]
        return most_recent_version_ids
