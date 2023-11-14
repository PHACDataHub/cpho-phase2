from django import forms
from django.contrib import messages
from django.forms.models import ModelForm
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from server.rules_framework import test_rule

from cpho.models import DimensionType, Indicator, Period, PHACOrg
from cpho.queries import (
    get_submission_statuses,
    relevant_dimension_types_for_period,
)
from cpho.text import tdt, tm
from cpho.util import get_lang_code, group_by

from .view_util import MustPassAuthCheckMixin, SinglePeriodMixin, export_mapper


# might need to move this to a form_fields.py file
class RelevantDimensionChoiceMultiCheckbox(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if get_lang_code() == "fr":
            return obj.name_fr
        return obj.name_en


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = [
            "name",
            "category",
            "topic",
            "detailed_indicator",
            "sub_indicator_measurement",
            "PHACOrg",
            "relevant_dimensions",
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

    topic = forms.ChoiceField(
        required=False,
        choices=Indicator.TOPIC_CHOICES,
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

    # make it display name_en attribute of DimensionType model
    relevant_dimensions = RelevantDimensionChoiceMultiCheckbox(
        required=False,
        queryset=DimensionType.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=DimensionType.objects.all(),
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

        data_for_periods = indicator.data.filter(
            period__in=relevant_periods, is_deleted=False
        )
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
        submission_statuses_by_period = {
            p: get_submission_statuses(indicator, p) for p in relevant_periods
        }

        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
            "data_counts_by_period": data_counts_by_period,
            "indicator": indicator,
            "submission_statuses_by_period": submission_statuses_by_period,
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
            self.indicator.data.filter(period=self.period, is_deleted=False)
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
            "dimension_types": relevant_dimension_types_for_period(
                self.indicator, self.period
            ),
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
