from typing import Any

from django import forms
from django.contrib import messages
from django.db.models.query import QuerySet
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

from ckeditor.widgets import CKEditorWidget
from phac_aspc.rules import test_rule

from cpho.models import DimensionType, Indicator, Period
from cpho.queries import (
    get_indicator_directories_for_user,
    get_indicators_for_user,
    get_metadata_submission_statuses,
    get_submission_statuses,
    relevant_dimension_types_for_period,
)
from cpho.text import tdt, tm
from cpho.util import get_lang_code, group_by

from .view_util import MustPassAuthCheckMixin, SinglePeriodMixin, export_mapper


# might need to move this to a form_fields.py file
class ModelMultipleChoiceFieldWithTranslation(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        if get_lang_code() == "fr":
            return obj.name_fr
        return obj.name_en


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        user = None
        if "user" in kwargs:
            user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        non_hso_readonly_fields = [
            "name",
            "category",
            "topic",
            "detailed_indicator",
            "sub_indicator_measurement",
            "relevant_dimensions",
            "relevant_period_types",
            "g1",
            "g2_lower",
            "g2_upper",
            "g3_lower",
            "g3_upper",
            "g4_lower",
            "g4_upper",
            "g5",
        ]
        if user and not test_rule("is_admin_or_hso", user):
            for field in non_hso_readonly_fields:
                self.fields[field].disabled = True

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
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

    relevant_period_types = forms.MultipleChoiceField(
        required=False,
        choices=Indicator.PERIOD_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
    )

    # make it display name_en attribute of DimensionType model
    relevant_dimensions = ModelMultipleChoiceFieldWithTranslation(
        required=False,
        queryset=DimensionType.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=DimensionType.objects.all(),
    )

    # GENERAL
    measure_text = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    impact_text = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    title_overall = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_overall = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    general_footnotes = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    main_source_english = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    other_relevant_sources_english = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    # SEX
    title_sex = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_sex = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    title_sex_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_sex_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # AGE
    title_age = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_age = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    title_age_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_age_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # PROVINCE/TERRITORY
    title_province_territory = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_province_territory = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    title_province_territory_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_province_territory_2 = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # LIVING ARRANGEMENT
    title_living_arrangement = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_living_arrangement = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # EDUCATION HOUSEHOLD
    title_education_household = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_education_household = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # INCOME QUINTILES
    title_income_quintiles = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_income_quintiles = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # TREND
    title_trend = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_trend = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    visual_description_trend = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    x_axis_trend = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    y_axis_trend = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    trend_footnotes = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    # BENCHMARKING
    title_benchmark = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    table_title_benchmark = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    x_axis_benchmark = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    benchmarking_footnotes = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )
    benchmarking_sources_english = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
    )

    # QUINTILES
    g1 = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g2_lower = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g2_upper = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g3_lower = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g3_upper = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g4_lower = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g4_upper = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    g5 = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    recommendations_for_hso = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            config_name="notes", attrs={"class": "form-control"}
        ),
        label=tm("recommendations_for_hso"),
    )

    pt_dynamic_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("pt_dynamic_text"),
    )

    hso_only_field_names = [
        "title_overall",
        "table_title_overall",
        "title_sex",
        "table_title_sex",
        "title_sex_2",
        "table_title_sex_2",
        "title_age",
        "table_title_age",
        "title_age_2",
        "table_title_age_2",
        "title_province_territory",
        "table_title_province_territory",
        "pt_dynamic_text",
        "title_province_territory_2",
        "table_title_province_territory_2",
        "title_living_arrangement",
        "table_title_living_arrangement",
        "title_education_household",
        "table_title_education_household",
        "title_income_quintiles",
        "table_title_income_quintiles",
        "title_trend",
        "table_title_trend",
        "visual_description_trend",
        "x_axis_trend",
        "y_axis_trend",
        "title_benchmark",
        "table_title_benchmark",
        "x_axis_benchmark",
    ]


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"

    def get_queryset(self):
        if test_rule("is_admin_or_hso", self.request.user):
            return Indicator.objects.all().order_by("name")

        else:
            filtered = get_indicators_for_user(self.request.user.id)
            filtered = list(filtered)
            filtered.sort(key=lambda i: i.name)
            return filtered

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "user_indicator_directories": get_indicator_directories_for_user(
                self.request.user.id
            ),
        }


class ViewIndicator(MustPassAuthCheckMixin, TemplateView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"

    def check_rule(self):
        return test_rule(
            "can_access_indicator",
            self.request.user,
            self.indicator,
        )

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        indicator = Indicator.objects.get(pk=self.kwargs["pk"])
        relevant_periods = indicator.get_relevant_periods()

        all_data = indicator.data.filter(is_deleted=False).prefetch_related(
            "period"
        )
        periods_with_data = set(d.period for d in all_data)

        all_shown_periods = periods_with_data | set(relevant_periods)

        data_counts_by_period = {
            p: len([datum for datum in all_data if datum.period_id == p.id])
            for p in all_shown_periods
        }
        submission_statuses_by_period = {
            p: get_submission_statuses(indicator, p) for p in all_shown_periods
        }

        alternate_periods = (
            set(indicator.get_adjacent_periods()) - periods_with_data
        )

        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
            "data_counts_by_period": data_counts_by_period,
            "indicator": indicator,
            "submission_statuses_by_period": submission_statuses_by_period,
            "metadata_submission_statuses": get_metadata_submission_statuses(
                indicator
            ),
            "alternate_periods": alternate_periods,
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
            "can_access_indicator",
            self.request.user,
            self.indicator,
        )


class CreateIndicator(MustPassAuthCheckMixin, CreateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/create_indicator.jinja2"

    def get_success_url(self):
        messages.success(self.request, tm("saved_successfully"))
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
        messages.success(self.request, tm("saved_successfully"))
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["pk"])
