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

from server.rules_framework import test_rule

from cpho.constants import SUBMISSION_STATUSES
from cpho.models import (
    Benchmarking,
    Country,
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
)
from cpho.queries import (
    get_submission_statuses,
    relevant_dimension_types_for_period,
)
from cpho.text import tdt, tm

from .view_util import (
    DimensionTypeOrAllMixin,
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
)


class BenchmarkingForm(ModelForm):
    class Meta:
        model = Benchmarking
        fields = [
            "oecd_country",
            "value",
            "year",
            "standard_deviation",
            "comparison_to_oecd_avg",
            "labels",
            "is_deleted",
        ]

    oecd_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    value = forms.FloatField(
        required=True,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tdt("Value")}
        ),
    )
    year = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    standard_deviation = forms.FloatField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    comparison_to_oecd_avg = forms.ChoiceField(
        required=True,
        choices=Benchmarking.COMPARISON_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    labels = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    is_deleted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
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

    def clean_standard_deviation(self):
        standard_deviation = self.cleaned_data["standard_deviation"]

        if standard_deviation is not None:
            if standard_deviation < -3000 or standard_deviation > 1000:
                self.add_error(
                    "standard_deviation",
                    tdt("Standard deviation must be a valid number"),
                )
        else:
            self.add_error(
                "standard_deviation", tdt("Standard deviation cannot be null")
            )

        return standard_deviation

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
            "can_edit_indicator_data", self.request.user, self.indicator
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
            messages.success(self.request, tdt("Benchmarking data saved"))
            return redirect(
                reverse(
                    "manage_benchmarking_data",
                    kwargs={"indicator_id": self.indicator.id},
                )
            )
        else:
            print(formset.errors)
            messages.error(
                self.request, tdt("There was an error saving the data")
            )
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicator"] = self.indicator
        context["benchmarking_formset"] = self.benchmarking_formset()
        return context
