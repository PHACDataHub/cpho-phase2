from django.db import models

from server import fields
from server.model_util import (add_to_admin, track_versions_with_editor,
                               track_versions_with_editor_and_approval)


@add_to_admin
@track_versions_with_editor
class DimensionType(models.Model):
    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    code = fields.CharField(max_length=50)  # codes are dev-friendly


@add_to_admin
@track_versions_with_editor
class DimensionValue(models.Model):
    dimension_type = fields.ForeignKey(
        DimensionType, on_delete=models.RESTRICT
    )

    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    value = fields.CharField(
        max_length=50
    )  # value is the 'unilingual' version, this can be useful for data-processing

    order = fields.FloatField(default=0.0)


@add_to_admin
@track_versions_with_editor
class Period(models.Model):
    year = fields.IntegerField()

    name_en = fields.CharField(max_length=50)

    name_fr = fields.CharField(max_length=50)

    class Meta:
        ordering = ["year"]
