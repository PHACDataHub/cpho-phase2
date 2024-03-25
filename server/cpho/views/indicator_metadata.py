import re
from datetime import datetime
from typing import Any

from django import forms
from django.contrib import messages
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView

from phac_aspc.rules import test_rule

from cpho.constants import SUBMISSION_STATUSES
from cpho.models import (
    Benchmarking,
    Country,
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    TrendAnalysis,
)
from cpho.text import tdt, tm

from .view_util import (
    BaseInlineFormSetWithUniqueTogetherCheck,
    DimensionTypeOrAllMixin,
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
)


class BenchmarkingForm(ModelForm):
    class Meta:
        model = Benchmarking
        fields = [
            "unit",
            "oecd_country",
            "value",
            "year",
            "comparison_to_oecd_avg",
            "labels",
            "is_deleted",
        ]

    unit = forms.ChoiceField(
        required=False,
        choices=Benchmarking.UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("unit"),
    )
    oecd_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("oecd_country"),
    )

    value = forms.FloatField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tm("value")}
        ),
        label=tm("value"),
    )
    year = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("year"),
    )

    comparison_to_oecd_avg = forms.ChoiceField(
        required=True,
        choices=Benchmarking.COMPARISON_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("comparison_to_oecd_average"),
    )
    labels = forms.ChoiceField(
        required=False,
        choices=Benchmarking.LABEL_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("labels"),
    )
    is_deleted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=tm("delete"),
    )

    def clean_comparison_to_oecd_avg(self):
        comparison_to_oecd_avg = self.cleaned_data["comparison_to_oecd_avg"]
        if not comparison_to_oecd_avg:
            self.add_error(
                "comparison_to_oecd_avg",
                tdt("Please select a comparison option"),
            )

        return comparison_to_oecd_avg

    def clean_oecd_country(self):
        oecd_country = self.cleaned_data["oecd_country"]
        if not oecd_country:
            self.add_error("oecd_country", tdt("Please select a country"))

        return oecd_country

    def clean_value(self):
        value = self.cleaned_data["value"]
        if value and value < 0:
            self.add_error("value", tdt("Value cannot be negative"))
        return value

    def clean_year(self):
        year = self.cleaned_data["year"]

        if year is None or year == "":
            return None

        if year:
            try:
                if not (int(year) >= 2000 and int(year) <= 2050):
                    self.add_error(
                        "year",
                        tdt("Year must be between the years 2000 and 2050"),
                    )
            except ValueError:
                self.add_error(
                    "year",
                    tdt("Year must be a valid number"),
                )

        return year

    def save(self, commit=True):
        if self.cleaned_data["is_deleted"]:
            self.instance.deletion_time = str(datetime.now())
        return super().save(commit=commit)


class ManageBenchmarkingData(MustPassAuthCheckMixin, TemplateView):
    template_name = "benchmarking/manage_benchmarking_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def check_rule(self):
        return test_rule(
            "can_edit_benchmarking", self.request.user, self.indicator
        )

    def benchmarking_formset(self):
        existing_data = Benchmarking.active_objects.filter(
            indicator=self.indicator
        ).order_by("oecd_country__name_en", "year")

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            Benchmarking,
            fk_name="indicator",
            form=BenchmarkingForm,
            extra=1,
            can_delete=False,
            formset=BaseInlineFormSetWithUniqueTogetherCheck,
        )

        kwargs = {
            "instance": self.indicator,
            "queryset": existing_data,
            "prefix": "benchmarking",
        }

        if self.request.method == "POST":
            fs = InlineFormsetCls(self.request.POST, **kwargs)
        else:
            fs = InlineFormsetCls(**kwargs)

        for form in fs:
            form.instance.indicator = self.indicator

        return fs

    def post(self, *args, **kwargs):
        formset = self.benchmarking_formset()
        if formset.is_valid():
            formset.save()
            messages.success(self.request, tm("saved_successfully"))
            return redirect(
                reverse(
                    "manage_benchmarking_data",
                    kwargs={"indicator_id": self.indicator.id},
                )
            )
        else:
            print(formset.errors)
            messages.error(self.request, tm("error_saving_form"))
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicator"] = self.indicator
        context["benchmarking_formset"] = self.benchmarking_formset()
        return context


class TrendAnalysisForm(ModelForm):
    class Meta:
        model = TrendAnalysis
        fields = [
            "year",
            "data_point",
            "line_of_best_fit_point",
            "trend_segment",
            "trend",
            "is_deleted",
            "data_quality",
            "data_point_lower_ci",
            "data_point_upper_ci",
            "unit",
        ]

    year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("year"),
    )

    data_point = forms.FloatField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_point"),
    )

    line_of_best_fit_point = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("line_of_best_fit_point"),
    )

    trend_segment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("trend_segment"),
    )

    trend = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.TREND_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("trend"),
    )

    data_quality = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.DATA_QUALITY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("data_quality"),
    )

    unit = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("unit"),
    )

    data_point_lower_ci = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_lower_ci"),
    )

    data_point_upper_ci = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_upper_ci"),
    )

    is_deleted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=tm("delete"),
    )

    def clean_year(self):
        year = self.cleaned_data["year"]

        if year is None or year == "":
            return None

        year = year.strip().replace(" ", "")

        single_year = re.match(r"^\d{4}$", year)
        multi_year = re.match(r"^\d{4}-\d{4}$", year)

        if not single_year and not multi_year:
            self.add_error(
                "year",
                tm("year_format"),
            )
            return year

        if single_year:
            if not (int(year) >= 2000 and int(year) <= 2050):
                self.add_error(
                    "year",
                    tm("year_timeframe_between"),
                )

        else:
            start_year, end_year = map(int, year.split("-"))
            if not (2000 <= start_year <= end_year <= 2050):
                self.add_error(
                    "year",
                    tm("year_timeframe_between_multi"),
                )

        return year

    def clean_trend_segment(self):
        trend_segment = self.cleaned_data["trend_segment"]

        if trend_segment is None or trend_segment == "":
            return None

        if trend_segment:
            trend_segment_ = trend_segment.strip().replace(" ", "")
            single_segment = re.match(r"^\d{4}-\d{4}$", trend_segment_)
            multi_segment = re.match(
                r"^\d{4}-\d{4}to\d{4}-\d{4}$", trend_segment_
            )
            if not single_segment and not multi_segment:
                self.add_error(
                    "trend_segment",
                    tm("trend_segment_format"),
                )
                return trend_segment
            if single_segment:
                start_year, end_year = map(int, trend_segment_.split("-"))
                if not (2000 <= start_year <= end_year <= 2050):
                    self.add_error(
                        "trend_segment",
                        tm("trend_timeframe_between"),
                    )

            else:
                start_range, end_range = map(str, trend_segment_.split("to"))
                start_year_start, start_year_end = map(
                    int, start_range.split("-")
                )
                end_year_start, end_year_end = map(int, end_range.split("-"))
                if not (
                    2000
                    <= start_year_start
                    <= start_year_end
                    <= end_year_start
                    <= end_year_end
                    <= 2050
                ):
                    self.add_error(
                        "trend_segment",
                        tm("trend_timeframe_between_multi"),
                    )
            return trend_segment

    def save(self, commit=True):
        if self.cleaned_data["is_deleted"]:
            self.instance.deletion_time = str(datetime.now())
        return super().save(commit=commit)


class ManageTrendAnalysisData(MustPassAuthCheckMixin, TemplateView):
    template_name = "trend_analysis/manage_trend_analysis_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def check_rule(self):
        return test_rule(
            "can_edit_trend_analysis", self.request.user, self.indicator
        )

    def trend_analysis_formset(self):
        existing_data = TrendAnalysis.active_objects.filter(
            indicator=self.indicator
        ).order_by("year")

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            TrendAnalysis,
            fk_name="indicator",
            form=TrendAnalysisForm,
            extra=1,
            can_delete=False,
            formset=BaseInlineFormSetWithUniqueTogetherCheck,
        )

        kwargs = {
            "instance": self.indicator,
            "queryset": existing_data,
            "prefix": "trend_analysis",
        }

        if self.request.method == "POST":
            fs = InlineFormsetCls(self.request.POST, **kwargs)
        else:
            fs = InlineFormsetCls(**kwargs)

        for form in fs:
            form.instance.indicator = self.indicator

        return fs

    def post(self, *args, **kwargs):
        formset = self.trend_analysis_formset()
        if formset.is_valid():
            formset.save()
            messages.success(self.request, tm("saved_successfully"))
            return redirect(
                reverse(
                    "manage_trend_analysis_data",
                    kwargs={"indicator_id": self.indicator.id},
                )
            )
        else:
            print(formset.errors)
            messages.error(self.request, tm("error_saving_form"))
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicator"] = self.indicator
        context["trend_analysis_formset"] = self.trend_analysis_formset()
        return context
