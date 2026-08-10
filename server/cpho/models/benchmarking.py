from django.db import models

from data_fetcher.core import DataFetcher

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor_and_submission,
)

from cpho.text import tm

from .indicator import Indicator
from .model_util import (
    ActiveObjManager,
    SubmissionHelpersMixin,
    SubmissionQueryset,
)


class BenchmarkLiveNameFetcher(DataFetcher):
    """
    changelog won't prefetch related fields
    so we define a live-name fetcher
    """

    def batch_load_dict(self, keys):
        data = Benchmarking.objects.filter(id__in=keys).prefetch_related(
            "indicator", "oecd_country"
        )
        by_id = {datum.id: datum.__str__() for datum in data}
        return by_id


@add_to_admin
@track_versions_with_editor_and_submission
class Benchmarking(models.Model, SubmissionHelpersMixin):
    changelog_live_name_fetcher_class = BenchmarkLiveNameFetcher

    class Meta:
        unique_together = [
            (
                "indicator",
                "oecd_country",
                "is_deleted",
                "deletion_time",
                "labels",
            ),
        ]
        verbose_name = tm("benchmarking")
        verbose_name_plural = tm("benchmarking")

    objects = models.Manager.from_queryset(SubmissionQueryset)()
    active_objects = ActiveObjManager.from_queryset(SubmissionQueryset)()
    indicator = fields.ForeignKey(
        Indicator, on_delete=models.CASCADE, related_name="benchmarking"
    )
    UNIT_CHOICES = [
        ("", "--"),
        ("ddd_per_1000_per_day", tm("ddd_per_1000_per_day")),
        (
            "deaths_per_million_inhabitants",
            tm("deaths_per_million_inhabitants"),
        ),
        ("percent", tm("percent")),
        ("rate_per_100k_population", tm("rate_per_100k_population")),
        ("rate_per_1000_population", tm("rate_per_1000_population")),
        ("litres_per_person", tm("litres_per_person")),
        ("years", tm("years")),
    ]
    unit = fields.CharField(
        max_length=50, choices=UNIT_CHOICES, blank=True, null=True
    )
    oecd_country = fields.ForeignKey(
        "cpho.Country", on_delete=models.RESTRICT, blank=True, null=True
    )
    value = fields.FloatField(blank=True, null=True)
    year = fields.CharField(max_length=50, blank=True, null=True)
    # standard_deviation = fields.FloatField(null=True)

    COMPARISON_CHOICES = [
        ("", "--"),
        ("better", tm("better")),
        ("similar", tm("similar")),
        ("worse", tm("worse")),
        ("outlier", tm("outlier")),
    ]
    comparison_to_oecd_avg = fields.CharField(
        max_length=50, choices=COMPARISON_CHOICES, blank=True, null=True
    )

    LABEL_CHOICES = [
        ("", "--"),
        ("anxiety", tm("anxiety")),
        ("depression", tm("depression")),
        ("women", tm("women")),
        ("men", tm("men")),
        ("male", tm("male")),
        ("female", tm("female")),
    ]
    labels = fields.CharField(
        max_length=50, blank=True, null=True, choices=LABEL_CHOICES
    )
    methodology_differences = fields.BooleanField(default=False)
    is_deleted = fields.BooleanField(default=False)
    deletion_time = fields.CharField(
        max_length=50, blank=True, null=True, default=""
    )

    def __str__(self):
        return str(self.indicator) + " : " + str(self.oecd_country)
