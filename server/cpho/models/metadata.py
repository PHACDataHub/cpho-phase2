from django.db import models

from server import fields
from server.model_util import add_to_admin

from cpho.constants import HSO_APPROVAL_TYPE, PROGRAM_APPROVAL_TYPE
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
    approval_type = models.CharField(
        max_length=20,
        choices=[
            (HSO_APPROVAL_TYPE, tdt("HSO")),
            (PROGRAM_APPROVAL_TYPE, tdt("Surveillance Program")),
        ],
    )
