import csv
from typing import Any, Dict

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
    View,
)

from server.rules_framework import test_rule

from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDataSubmission,
    IndicatorDatum,
    Period, PHACOrg,
)
from cpho.queries import get_submission_statuses
from cpho.text import tdt, tm
from cpho.util import group_by

from .view_util import MustPassAuthCheckMixin, SinglePeriodMixin, export_mapper


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = [
            "name",
            "category",
            "sub_category",
            "detailed_indicator",
            "sub_indicator_measurement",
            "PHACOrg",
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

    PHACOrg = forms.ModelChoiceField(
        required=False,
        queryset=PHACOrg.branches(),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


class ViewIndicator(MustPassAuthCheckMixin, TemplateView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"

    def check_rule(self):
        return test_rule(
            "can_view_indicator_data",
            self.request.user,
            self.indicator,
        )

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

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


class ViewIndicatorForPeriod(
    MustPassAuthCheckMixin, SinglePeriodMixin, DetailView
):
    model = Indicator
    template_name = "indicators/view_indicator_for_period.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

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
                self.indicator, self.period
            ),
            "indicator_data_by_dimension_type": self.indicator_data_by_dimension_type,
        }

    def check_rule(self):
        return test_rule(
            "can_view_indicator_data",
            self.request.user,
            self.indicator,
        )


class CreateIndicator(MustPassAuthCheckMixin, CreateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/create_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }

    def check_rule(self):
        return test_rule(
            "can_create_indicator",
            self.request.user,
        )


class EditIndicator(MustPassAuthCheckMixin, UpdateView):
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

    def check_rule(self):
        return test_rule(
            "can_edit_indicator",
            self.request.user,
            self.indicator,
        )
    
    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

class ExportIndicator(View):
    
    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])
    
    def get(self,request, *args, **kwargs):
        indicator = self.indicator

    #     print("Queried Indicator Data:")
    #     #for data in 
    #     relevant_records=IndicatorDatum.objects.filter(indicator=self.indicator)
    #    #print(relevant_records)

    #     for record in relevant_records:
    #         print(indicator.name)


        response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="indicator_data.csv"'},
        )

        writer = csv.writer(response)
        header_row=["Indicator", "Detailed Indicator", "Sub_Indicator_Measurement", "Category", "Topic", "Data_Quality","Value", "Value_LowerCI", "Value_UpperCI", "SingleYear_TimeFrame","MultiYear_TimeFrame", "Value_Units", "Dimension_Type", "Dimension_Value"]
        writer.writerow(header_row)

        mapper = export_mapper()

        for record in IndicatorDatum.objects.filter(indicator=self.indicator):               

                writer.writerow([
                    indicator.name,
                    indicator.detailed_indicator,
                    indicator.sub_indicator_measurement,
                    mapper["category_mapper"].get(indicator.category, ""),
                    mapper["subcategory_mapper"].get(indicator.sub_category, ""),
                    mapper["data_quality_mapper"].get(record.data_quality, ""),
                    record.value,
                    record.value_lower_bound,
                    record.value_upper_bound,
                    record.single_year_timeframe,
                    record.multi_year_timeframe,
                    mapper["value_unit_mapper"].get(record.value_unit),
                    mapper["dimension_type_mapper"].get(record.dimension_type, ""),
                    mapper["non_literal_dimension_value_mapper"].get(record.dimension_value, "")
                ])

        return response
    

