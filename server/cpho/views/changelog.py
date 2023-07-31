from typing import Any, Dict

from django import forms
from django.core.exceptions import FieldDoesNotExist
from django.views.generic import TemplateView

from cpho import models
from cpho.util import flatten

changelog_models = [models.Indicator, models.IndicatorDatum]

from versionator.changelog.simple_changelog import create_simple_changelog


class GlobalChangelog(TemplateView):
    template_name = "changelog/global_changelog.jinja2"

    def get_page_size(self):
        return 50

    def get_context_data(self, **kwargs):
        page_num = self.kwargs.get("page_num", 1)
        changelog = create_simple_changelog(
            changelog_models, page_size=self.get_page_size()
        )
        data = changelog.get_page(1)

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
