from django.db import models

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_approval,
)

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
    year = fields.IntegerField()

    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    class Meta:
        ordering = ["year"]

    @property
    def name(self):
        return getattr(self, f"name_{get_lang_code()}")
