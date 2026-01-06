from typing import Any, Dict

from django import forms
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.views.generic import TemplateView

from phac_aspc.rules import test_rule

from cpho import models
from cpho.util import flatten

from .view_util import MustBeAdminOrHsoMixin, MustPassAuthCheckMixin

changelog_models = [
    models.Indicator,
    models.IndicatorDatum,
    models.Benchmarking,
    models.TrendAnalysis,
]

global_changelog_models = [
    models.DimensionType,
    models.DimensionValue,
    *changelog_models,
]

from versionator.changelog import Changelog, ChangelogConfig


class ChangelogView(TemplateView):
    def get_changelog_object(self):
        raise NotImplementedError()

    def get_page_size(self):
        return 25

    def get_context_data(self, **kwargs):
        page_num = self.kwargs.get("page_num", 1)
        changelog_object = self.get_changelog_object()
        entries = changelog_object.get_entries(page_num)
        num_pages = changelog_object.get_page_count()

        ctx = {
            "edit_entries": entries,
            "has_next_page": page_num < num_pages,
            "num_pages": num_pages,
            "page_num": page_num,
        }

        if page_num < num_pages:
            ctx["next_page_num"] = page_num + 1

        if page_num > 1:
            ctx["prev_page_num"] = page_num - 1

        return ctx


class GlobalChangelog(ChangelogView, MustBeAdminOrHsoMixin):
    template_name = "changelog/global_changelog.jinja2"

    def get_changelog_object(self):

        changelog_config = ChangelogConfig(
            global_changelog_models,
            page_size=self.get_page_size(),
        )

        return Changelog(changelog_config)


class IndicatorScopedChangelog(ChangelogView, MustPassAuthCheckMixin):
    template_name = "changelog/indicator_scoped_changelog.jinja2"

    def check_rule(self):
        indicator = models.Indicator.objects.get(
            id=self.kwargs["indicator_id"]
        )
        return test_rule("can_access_indicator", self.request.user, indicator)

    def get_changelog_object(self):
        indicator_id = self.kwargs["indicator_id"]

        class IndicatorScopedConfig(ChangelogConfig):
            models = [
                models.Indicator,
                models.IndicatorDatum,
                models.Benchmarking,
                models.TrendAnalysis,
            ]

            def get_base_version_queryset_for_single_model(self, model):
                history_model = model._history_class

                if model in (
                    models.IndicatorDatum,
                    models.Benchmarking,
                    models.TrendAnalysis,
                ):
                    return history_model.objects.filter(
                        indicator_id=indicator_id
                    ).all()

                elif model == models.Indicator:
                    return history_model.objects.filter(
                        eternal_id=indicator_id
                    )
                else:
                    raise NotImplementedError("model not supported")

        config = IndicatorScopedConfig(page_size=self.get_page_size())

        return Changelog(config)

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

        class UserScopedConfig(ChangelogConfig):
            models = changelog_models

            def get_base_version_queryset_for_single_model(self, live_model):
                history_model = live_model._history_class
                return history_model.objects.filter(edited_by_id=user_id).all()

        config = UserScopedConfig(page_size=self.get_page_size())

        return Changelog(config)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "changelog_user": models.User.objects.get(
                id=self.kwargs["user_id"]
            ),
        }


class GlobalDatumChangelog(GlobalChangelog):
    def get_changelog_object(self):
        year = self.request.GET.get("year", None)
        if year:
            try:
                year = int(year)
            except ValueError:
                raise forms.ValidationError("Year must be an integer")

        class YearFilteredDatumConfig(ChangelogConfig):
            models = [models.IndicatorDatum]

            def get_base_version_queryset_for_single_model(self, live_model):
                history_model = live_model._history_class
                qs = history_model.objects.all()
                if year:
                    qs = qs.filter(period__year=year)
                return qs

        config = YearFilteredDatumConfig(page_size=self.get_page_size())

        return Changelog(config)
