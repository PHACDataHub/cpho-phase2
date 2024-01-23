from django.db import models

from server import fields
from server.model_util import add_to_admin

from cpho.constants import HSO_SUBMISSION_TYPE, PROGRAM_SUBMISSION_TYPE
from cpho.text import tdt, tm


@add_to_admin
class IndicatorDataSubmission(models.Model):
    submitted_by = fields.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
    )
    indicator = fields.ForeignKey("cpho.Indicator", on_delete=models.CASCADE)
    period = fields.ForeignKey("cpho.Period", on_delete=models.CASCADE)
    dimension_type = fields.ForeignKey(
        "cpho.DimensionType",
        on_delete=models.SET_NULL,
        null=True,
    )
    submission_type = models.CharField(
        max_length=20,
        choices=[
            (HSO_SUBMISSION_TYPE, tdt("HSO")),
            (PROGRAM_SUBMISSION_TYPE, tdt("Surveillance Program")),
        ],
    )


@add_to_admin
class PhacOrgRole(models.Model):
    user = fields.ForeignKey(
        "cpho.User", on_delete=models.CASCADE, related_name="phac_org_roles"
    )
    phac_org = fields.ForeignKey(
        "cpho.PHACOrg", on_delete=models.CASCADE, related_name="phac_org_roles"
    )
    is_phac_org_lead = models.BooleanField(default=False)


@add_to_admin
class IndicatorDirectory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    users = fields.ManyToManyField(
        "cpho.User",
        through="cpho.IndicatorDirectoryUserAccess",
        related_name="indicator_directories",
    )

    indicators = fields.ManyToManyField(
        "cpho.Indicator",
        through="cpho.IndicatorDirectoryLink",
        related_name="indicator_directories",
    )

    def __str__(self):
        return self.name


@add_to_admin
class IndicatorDirectoryLink(models.Model):
    """
    through model between an indicator and an indicator directory.
    """

    indicator = fields.ForeignKey(
        "cpho.Indicator",
        on_delete=models.CASCADE,
        related_name="indicator_directory_links",
    )
    directory = fields.ForeignKey(
        "cpho.IndicatorDirectory",
        on_delete=models.CASCADE,
        related_name="indicator_directory_links",
    )

    class Meta:
        unique_together = ("indicator", "directory")

    def __str__(self):
        return f"{self.directory} - {self.indicator}"


@add_to_admin
class IndicatorDirectoryUserAccess(models.Model):
    """
    through model between an indicator directory and a user
    """

    user = fields.ForeignKey(
        "cpho.User",
        on_delete=models.CASCADE,
        related_name="indicator_directory_user_accesses",
    )
    directory = fields.ForeignKey(
        "cpho.IndicatorDirectory",
        on_delete=models.CASCADE,
        related_name="indicator_directory_user_accesses",
    )

    class Meta:
        unique_together = ("user", "directory")

    def __str__(self):
        return f"{self.user} - {self.directory}"
