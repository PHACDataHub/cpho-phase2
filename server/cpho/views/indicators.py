from django import forms
from django.forms.models import ModelForm
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from cpho.models import DimensionType, Indicator
from cpho.text import tdt, tm
from cpho.util import dropdown_mapper

# import dictionary dropdown_mapper from file cpho\views\views_utils.py


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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    category = forms.ChoiceField(
        required=False,
        choices=[
            ("", "--"),
            ("factors_influencing_health", "Factors Influencing Health"),
            ("general_health_status", "General Health Status"),
            ("health_outcomes", "Health Outcomes"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    sub_category = forms.ChoiceField(
        required=False,
        choices=[
            ("", "--"),
            (
                "childhood_and_family_risk_and_protective_factors",
                "Childhood and Family Risk and Protective Factors",
            ),
            ("social_factors", "Social Factors"),
            ("substance_use", "Substance Use"),
            ("health_status", "Health Status"),
            (
                "chronic_diseases_and_mental_health",
                "Chronic Diseases and Mental Health",
            ),
            ("communicable_diseases", "Communicable Diseases"),
        ],
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
            "dropdown_mapper": dropdown_mapper(),
        }


class ViewIndicator(DetailView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
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
            "title_text": tdt("Create New Indicator"),
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
            "title_text": tdt("Edit Indicator") + ": " + self.object.name,
        }
