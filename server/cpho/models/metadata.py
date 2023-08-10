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
