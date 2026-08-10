from django.db import models

from cpho.constants import SUBMISSION_STATUSES


class SubmissionQueryset(models.QuerySet):
    def with_last_version_date(self):
        last_version_date = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("timestamp")[:1]
        )
        return self.annotate(last_version_date=last_version_date)

    def with_last_version_username(self, date_field="timestamp"):
        last_version_edited_by_username = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("edited_by__username")[:1]
        )
        return self.annotate(
            last_version_edited_by_username=last_version_edited_by_username
        )

    def with_last_version_id(self):
        last_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk")
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(last_version_id=last_version_id)

    def with_last_program_submitted_version_id(self):
        last_program_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_program_submitted=True,
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(
            last_program_submitted_version_id=last_program_submitted_version_id
        )

    def with_last_submitted_version_id(self):
        last_submitted_version_id = models.Subquery(
            self.model._history_class.objects.filter(
                eternal_id=models.OuterRef("pk"),
                is_hso_submitted=True,
            )
            .order_by("-timestamp")
            .values("id")[:1]
        )
        return self.annotate(
            last_submitted_version_id=last_submitted_version_id
        )

    def with_submission_annotations(self):
        return (
            self.with_last_version_id()
            .with_last_submitted_version_id()
            .with_last_program_submitted_version_id()
        )


class SubmissionHelpersMixin:
    def submission_status(self, submission_type):
        try:
            self.last_version_id
            self.last_submitted_version_id
            self.last_program_submitted_version_id
        except AttributeError:
            raise Exception("You must add the submission_annotations")

        if submission_type == "hso":
            if not self.last_submitted_version_id:
                return SUBMISSION_STATUSES.NOT_YET_SUBMITTED
            if self.last_version_id == self.last_submitted_version_id:
                return SUBMISSION_STATUSES.SUBMITTED
        elif submission_type == "program":
            if not self.last_program_submitted_version_id:
                return SUBMISSION_STATUSES.NOT_YET_SUBMITTED
            if self.last_version_id == self.last_program_submitted_version_id:
                return SUBMISSION_STATUSES.PROGRAM_SUBMITTED

        return SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION


class ActiveObjManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
