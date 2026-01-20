from typing import Any, Dict

from django import forms
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from phac_aspc.rules import test_rule

from server.form_util import StandardFormMixin

from cpho import models
from cpho.text import tm
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


class ChangelogFilterForm(StandardFormMixin):
    start_date = forms.DateField(
        label=tm("start_date"),
        required=False,
    )
    end_date = forms.DateField(
        label=tm("end_date"),
        required=False,
    )

    models = forms.MultipleChoiceField(
        label=tm("object_type"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[
            (m.__name__.lower(), m._meta.verbose_name)
            for m in changelog_models
        ],
    )


class ChangelogView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if settings.USE_SQLITE:
            raise Exception("Changelog is not supported on SQLite")

        return super().dispatch(request, *args, **kwargs)

    def get_changelog_config_class(self):
        return ChangelogConfig

    @cached_property
    def changelog_config(self):
        return self.get_changelog_config_class()(
            **self.get_changelog_config_kwargs()
        )

    def get_changelog_object(self):
        return Changelog(self.changelog_config)

    def get_changelog_config_kwargs(self) -> Dict[str, Any]:
        return {
            "page_size": self.get_page_size(),
        }

    def get_page_size(self):
        return 100

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

    @cached_property
    def filter_form(self):
        if self.request.GET:
            return ChangelogFilterForm(self.request.GET)
        return ChangelogFilterForm()

    def get_changelog_config_kwargs(self):
        kwargs = {
            **super().get_changelog_config_kwargs(),
            "models": global_changelog_models,
        }

        if not self.filter_form.is_valid():
            return kwargs

        if self.filter_form.cleaned_data.get("start_date"):
            kwargs["start_date"] = self.filter_form.cleaned_data["start_date"]

        if self.filter_form.cleaned_data.get("end_date"):
            kwargs["end_date"] = self.filter_form.cleaned_data["end_date"]

        if self.filter_form.cleaned_data.get("models"):
            model_names = self.filter_form.cleaned_data["models"]
            filtered_models = [
                m
                for m in changelog_models
                if m.__name__.lower() in model_names
            ]
            kwargs["models"] = filtered_models

        return kwargs

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "filter_form": self.filter_form,
        }


class IndicatorScopedChangelog(ChangelogView, MustPassAuthCheckMixin):
    template_name = "changelog/indicator_scoped_changelog.jinja2"

    def check_rule(self):
        indicator = models.Indicator.objects.get(
            id=self.kwargs["indicator_id"]
        )
        return test_rule("can_access_indicator", self.request.user, indicator)

    def get_changelog_config_class(self):

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

        return IndicatorScopedConfig

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

    def get_changelog_config_class(self):
        user_id = self.kwargs["user_id"]

        class UserScopedConfig(ChangelogConfig):
            models = changelog_models

            def get_base_version_queryset_for_single_model(self, live_model):
                history_model = live_model._history_class
                return history_model.objects.filter(edited_by_id=user_id).all()

        return UserScopedConfig

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "changelog_user": models.User.objects.get(
                id=self.kwargs["user_id"]
            ),
        }


class GlobalDatumChangelog(GlobalChangelog):

    def get_changelog_config_class(self):
        year = self.request.GET.get("year", None)

        if not year:
            return super().get_changelog_config_class()

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

        return YearFilteredDatumConfig

    def get_changelog_config_kwargs(self):
        return {
            **super().get_changelog_config_kwargs(),
            "models": [models.IndicatorDatum],
        }

    @cached_property
    def filter_form(self):
        f = super().filter_form
        f.fields.pop("models")
        return f
