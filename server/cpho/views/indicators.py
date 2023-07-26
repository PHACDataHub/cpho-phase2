import csv
from typing import Any

from django import forms
from django.contrib import messages
from django.forms.models import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from cpho.models import DimensionType, Indicator, Period
from cpho.queries import get_submission_statuses
from cpho.text import tdt, tm
from cpho.util import group_by

from .view_util import SinglePeriodMixin


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = [
            "name",
            "category",
            "sub_category",
            "detailed_indicator",
            "sub_indicator_measurement",
        ]

    name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    category = forms.ChoiceField(
        required=False,
        choices=Indicator.CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    sub_category = forms.ChoiceField(
        required=False,
        choices=Indicator.SUB_CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    detailed_indicator = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    sub_indicator_measurement = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


class ViewIndicator(TemplateView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"

    def get_context_data(self, **kwargs):
        indicator = Indicator.objects.get(pk=self.kwargs["pk"])
        relevant_periods = Period.relevant_years()

        data_for_periods = indicator.data.filter(period__in=relevant_periods)
        data_counts_by_period = {
            p: len(
                [
                    datum
                    for datum in data_for_periods
                    if datum.period_id == p.id
                ]
            )
            for p in relevant_periods
        }

        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
            "data_counts_by_period": data_counts_by_period,
            "indicator": indicator,
        }


class ViewIndicatorForPeriod(SinglePeriodMixin, DetailView):
    model = Indicator
    template_name = "indicators/view_indicator_for_period.jinja2"

    @cached_property
    def indicator(self):
        return self.object

    @cached_property
    def indicator_data(self):
        return (
            self.indicator.data.filter(period=self.period)
            .select_related("dimension_value")
            .prefetch_related("dimension_type")
            .with_submission_annotations()
            .with_last_version_date()
            .order_by("dimension_value")
        )

    @cached_property
    def indicator_data_by_dimension_type(self):
        return group_by(
            list(self.indicator_data), lambda d: d.dimension_type_id
        )

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
            "dimension_types": DimensionType.objects.all(),
            "submission_statuses": get_submission_statuses(
                self.object, self.period
            ),
            "indicator_data_by_dimension_type": self.indicator_data_by_dimension_type,
        }


class CreateIndicator(CreateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/create_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


class EditIndicator(UpdateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/edit_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "indicator": self.object,
        }
