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
    Countries,
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
        queryset=Countries.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    standard_deviation = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    comparison_to_oecd_avg = forms.ChoiceField(
        required=False,
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
