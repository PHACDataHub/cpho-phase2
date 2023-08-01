from typing import Any, Dict

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.views.generic import TemplateView

from cpho import models
from cpho.util import flatten

changelog_models = [models.Indicator, models.IndicatorDatum]

from versionator.changelog.consecutive_versions_fetcher import (
    ConsecutiveVersionsFetcher,
)
from versionator.changelog.simple_changelog import create_simple_changelog


class GlobalChangelog(TemplateView):
    template_name = "changelog/global_changelog.jinja2"

    def get_page_size(self):
        return 25

    def get_context_data(self, **kwargs):
        page_num = self.kwargs.get("page_num", 1)
        changelog = create_simple_changelog(
            changelog_models, page_size=self.get_page_size()
        )
        data = changelog.get_page(page_num)

        ctx = {
            "edit_entries": data["changelog_entries"],
            "has_next_page": data["has_next_page"],
            "num_pages": data["num_pages"],
            "page_num": page_num,
        }

        if page_num < data["num_pages"]:
            ctx["next_page_num"] = page_num + 1

        if page_num > 1:
            ctx["prev_page_num"] = page_num - 1

        return ctx


def get_indicator_scoped_fetcher_class(indicator_id: int):
    class IndicatorScopedFetcher(ConsecutiveVersionsFetcher):
        def get_base_version_qs_for_single_model(self, indicator_datum_model):
            if indicator_datum_model is not models.IndicatorDatum:
                raise Exception("This changelog only supports IndicatorDatum")

            history_model = indicator_datum_model._history_class
            return history_model.objects.filter(
                indicator_id=indicator_id
            ).all()

    return IndicatorScopedFetcher


class IndicatorScopedChangelog(TemplateView):
    template_name = "changelog/indicator_scoped_changelog.jinja2"

    def get_page_size(self):
        return 25

    def get_context_data(self, **kwargs):
        page_num = self.kwargs.get("page_num", 1)
        FetcherCls = get_indicator_scoped_fetcher_class(
            self.kwargs["indicator_id"]
        )
        changelog = create_simple_changelog(
            [models.IndicatorDatum],
            fetcher_class=FetcherCls,
            page_size=self.get_page_size(),
        )
        data = changelog.get_page(page_num)

        ctx = {
            "edit_entries": data["changelog_entries"],
            "has_next_page": data["has_next_page"],
            "num_pages": data["num_pages"],
            "page_num": page_num,
            "indicator": models.Indicator.objects.get(
                id=self.kwargs["indicator_id"]
            ),
        }

        if page_num < data["num_pages"]:
            ctx["next_page_num"] = page_num + 1

        if page_num > 1:
            ctx["prev_page_num"] = page_num - 1

        return ctx
