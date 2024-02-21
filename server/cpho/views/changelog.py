from typing import Any, Dict

from django import forms
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.views.generic import TemplateView

from server.rules_framework import test_rule

from cpho import models
from cpho.util import flatten

from .view_util import MustBeAdminOrHsoMixin, MustPassAuthCheckMixin

changelog_models = [
    models.Indicator,
    models.IndicatorDatum,
    models.Benchmarking,
]

from versionator.changelog.consecutive_versions_fetcher import (
    ConsecutiveVersionsFetcher,
)
from versionator.changelog.simple_changelog import create_simple_changelog


class ChangelogView(TemplateView):
    def get_changelog_object(self):
        raise NotImplementedError()

    def get_page_size(self):
        return 25

    def get_context_data(self, **kwargs):
        page_num = self.kwargs.get("page_num", 1)
        changelog_object = self.get_changelog_object()
        data = changelog_object.get_page(page_num)

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


class GlobalChangelog(ChangelogView, MustBeAdminOrHsoMixin):
    template_name = "changelog/global_changelog.jinja2"

    def get_changelog_object(self):
        return create_simple_changelog(
            changelog_models, page_size=self.get_page_size()
        )


class IndicatorScopedChangelog(ChangelogView, MustPassAuthCheckMixin):
    template_name = "changelog/indicator_scoped_changelog.jinja2"

    def check_rule(self):
        indicator = models.Indicator.objects.get(
            id=self.kwargs["indicator_id"]
        )
        return test_rule("can_access_indicator", self.request.user, indicator)

    def get_changelog_object(self):
        indicator_id = self.kwargs["indicator_id"]

        class IndicatorScopedFetcher(ConsecutiveVersionsFetcher):
            def get_base_version_qs_for_single_model(
                self, indicator_datum_model
            ):
                if indicator_datum_model is not models.IndicatorDatum:
                    raise Exception(
                        "This changelog only supports IndicatorDatum"
                    )

                history_model = indicator_datum_model._history_class
                return history_model.objects.filter(
                    indicator_id=indicator_id
                ).all()

        return create_simple_changelog(
            [models.IndicatorDatum],
            fetcher_class=IndicatorScopedFetcher,
            page_size=self.get_page_size(),
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "indicator": models.Indicator.objects.get(
                id=self.kwargs["indicator_id"]
            ),
        }


class UserScopedChangelog(ChangelogView):
    template_name = "changelog/user_scoped_changelog.jinja2"

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.id != self.kwargs["user_id"]:
            if not test_rule("is_admin_or_hso", self.request.user):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get_changelog_object(self):
        user_id = self.kwargs["user_id"]

        class UserScopedFetcher(ConsecutiveVersionsFetcher):
            def get_base_version_qs_for_single_model(self, live_model):
                history_model = live_model._history_class
                return history_model.objects.filter(edited_by_id=user_id).all()

        return create_simple_changelog(
            [models.Indicator, models.IndicatorDatum, models.Benchmarking],
            fetcher_class=UserScopedFetcher,
            page_size=self.get_page_size(),
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "changelog_user": models.User.objects.get(
                id=self.kwargs["user_id"]
            ),
        }
