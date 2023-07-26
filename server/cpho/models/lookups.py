from django.conf import settings
from django.db import models

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_submission,
)

from cpho.text import tdt
from cpho.util import get_lang_code


@add_to_admin
@track_versions_with_editor
class DimensionType(models.Model):
    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    code = fields.CharField(max_length=50)  # codes are dev-friendly

    is_literal = models.BooleanField(default=False)

    @property
    def name(self):
        return getattr(self, f"name_{get_lang_code()}")

    def __str__(self):
        return " ".join(
            [
                str(self.code),
            ]
        )


@add_to_admin
@track_versions_with_editor
class DimensionValue(models.Model):
    dimension_type = fields.ForeignKey(
        DimensionType,
        on_delete=models.RESTRICT,
        related_name="possible_values",
    )

    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    value = fields.CharField(
        max_length=50
    )  # value is the 'unilingual' version, this can be useful for data-processing

    order = fields.FloatField(default=0.0)

    @property
    def name(self):
        return getattr(self, f"name_{get_lang_code()}")

    def __str__(self):
        return " ".join(
            [
                str(self.value),
            ]
        )


@add_to_admin
@track_versions_with_editor
class Period(models.Model):
    CALENDAR_YEAR_TYPE = "calendar"
    FISCAL_YEAR_TYPE = "fiscal"
    YEAR_TYPE_CHOICES = (
        (CALENDAR_YEAR_TYPE, tdt("Calendar")),
        (FISCAL_YEAR_TYPE, tdt("Fiscal")),
    )

    year = fields.IntegerField()
    quarter = fields.IntegerField(null=True, blank=True)
    year_type = fields.CharField(
        max_length=50, choices=YEAR_TYPE_CHOICES, null=True, blank=True
    )

    class Meta:
        ordering = ["year", "quarter"]
        unique_together = ["year", "quarter", "year_type"]

    @property
    def name(self):
        return getattr(self, f"name_{get_lang_code()}")

    def as_tuple(self):
        # can be used for sorting
        # python's default sort will stably sort by year, then quarter
        return (self.year, self.quarter)

    def __str__(self):
        s = str(self.year)
        if self.year_type == self.FISCAL_YEAR_TYPE:
            s = f"FY {s}"
        if self.quarter:
            s = f"{s} Q{self.quarter}"
        return s

    @staticmethod
    def relevant_years():
        return Period.objects.filter(year=settings.CURRENT_YEAR)
