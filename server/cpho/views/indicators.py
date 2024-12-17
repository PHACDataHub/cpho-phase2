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

from .view_util import (
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
    age_group_sort,
    export_mapper,
)


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

        if user and not test_rule("is_admin_or_hso", user):
            for field in self.non_hso_readonly_fields:
                self.fields[field].disabled = True

        fr_fields = [field for field in self.fields if field.endswith("_fr")]
        self.hso_only_field_names = self.hso_only_field_names + fr_fields

    def charField(required=False, french=False, label=None):
        class_string = "form-control"
        if french:
            class_string += " fr-field"

        return forms.CharField(
            required=required,
            widget=forms.TextInput(attrs={"class": class_string}),
            label=label if label else None,
        )

    def ckEditorField(required=False, french=False, label=None):
        class_string = "form-control"
        if french:
            class_string += " fr-field"

        return forms.CharField(
            required=required,
            widget=CKEditorWidget(
                config_name="notes", attrs={"class": class_string}
            ),
            label=label if label else None,
        )

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

    hso_only_field_names = [
        "title_overall",
        "table_title_overall",
        "title_sex",
        "table_title_sex",
        "title_age",
        "table_title_age",
        "title_province_territory",
        "table_title_province_territory",
        "pt_dynamic_text",
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
        "benchmarking_dynamic_text",
        "sdg_goal",
        "y_axis_trend_min",
        "y_axis_trend_max",
    ]
    name = charField(required=True, label=tm("name"))
    name_fr = charField(french=True, label=tm("name_french"))

    category = forms.ChoiceField(
        required=False,
        choices=Indicator.CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("category"),
    )

    topic = forms.ChoiceField(
        required=False,
        choices=Indicator.TOPIC_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("topic"),
    )

    detailed_indicator = charField(label=tm("detailed_indicator"))
    detailed_indicator_fr = charField(
        french=True, label=tm("detailed_indicator_french")
    )

    sub_indicator_measurement = charField(
        label=tm("sub_indicator_measurement")
    )
    sub_indicator_measurement_fr = charField(
        french=True, label=tm("sub_indicator_measurement_french")
    )

    relevant_period_types = forms.MultipleChoiceField(
        required=False,
        choices=Indicator.PERIOD_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label=tm("relevant_period_types"),
    )

    # make it display name_en attribute of DimensionType model
    relevant_dimensions = ModelMultipleChoiceFieldWithTranslation(
        required=False,
        queryset=DimensionType.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        initial=DimensionType.objects.all(),
        label=tm("relevant_dimensions"),
    )

    # GENERAL
    measure_text = charField(label=tm("measure_text"))
    measure_text_fr = charField(french=True, label=tm("measure_text_french"))

    impact_text = ckEditorField(label=tm("impact_text"))
    impact_text_fr = ckEditorField(french=True, label=tm("impact_text_french"))

    title_overall = charField(label=tm("title_overall"))
    title_overall_fr = charField(french=True, label=tm("title_overall_french"))

    table_title_overall = charField(label=tm("table_title_overall"))
    table_title_overall_fr = charField(
        french=True, label=tm("table_title_overall_french")
    )

    sdg_goal = ckEditorField(label=tm("sdg_goal"))
    sdg_goal_fr = ckEditorField(french=True, label=tm("sdg_goal_french"))

    general_footnotes = ckEditorField(label=tm("general_footnotes"))
    general_footnotes_fr = ckEditorField(
        french=True, label=tm("general_footnotes_french")
    )

    main_source_english = ckEditorField(label=tm("main_source_english"))
    main_source_fr = ckEditorField(french=True, label=tm("main_source_french"))

    other_relevant_sources_english = ckEditorField(
        label=tm("other_relevant_sources_english")
    )
    other_relevant_sources_fr = ckEditorField(
        french=True, label=tm("other_relevant_sources_french")
    )

    recommendations_for_hso = ckEditorField(
        label=tm("recommendations_for_hso")
    )
    recommendations_for_hso_fr = ckEditorField(
        french=True, label=tm("recommendations_for_hso_french")
    )

    # SEX
    title_sex = charField(label=tm("title_sex"))
    title_sex_fr = charField(french=True, label=tm("title_sex_french"))

    table_title_sex = charField(label=tm("table_title_sex"))
    table_title_sex_fr = charField(
        french=True, label=tm("table_title_sex_french")
    )

    # AGE
    title_age = charField(label=tm("title_age"))
    title_age_fr = charField(french=True, label=tm("title_age_french"))

    table_title_age = charField(label=tm("table_title_age"))
    table_title_age_fr = charField(
        french=True, label=tm("table_title_age_french")
    )

    # PROVINCE/TERRITORY
    title_province_territory = charField(label=tm("title_province_territory"))
    title_province_territory_fr = charField(
        french=True, label=tm("title_province_territory_french")
    )

    table_title_province_territory = charField(
        label=tm("table_title_province_territory")
    )
    table_title_province_territory_fr = charField(
        french=True, label=tm("table_title_province_territory_french")
    )

    pt_dynamic_text = charField(label=tm("pt_dynamic_text"))
    pt_dynamic_text_fr = charField(
        french=True, label=tm("pt_dynamic_text_french")
    )

    # LIVING ARRANGEMENT
    title_living_arrangement = charField(label=tm("title_living_arrangement"))
    title_living_arrangement_fr = charField(
        french=True, label=tm("title_living_arrangement_french")
    )

    table_title_living_arrangement = charField(
        label=tm("table_title_living_arrangement")
    )
    table_title_living_arrangement_fr = charField(
        french=True, label=tm("table_title_living_arrangement_french")
    )

    # EDUCATION HOUSEHOLD
    title_education_household = charField(
        label=tm("title_education_household")
    )
    title_education_household_fr = charField(
        french=True, label=tm("title_education_household_french")
    )

    table_title_education_household = charField(
        label=tm("table_title_education_household")
    )
    table_title_education_household_fr = charField(
        french=True, label=tm("table_title_education_household_french")
    )

    # INCOME QUINTILES
    title_income_quintiles = charField(label=tm("title_income_quintiles"))
    title_income_quintiles_fr = charField(
        french=True, label=tm("title_income_quintiles_french")
    )

    table_title_income_quintiles = charField(
        label=tm("table_title_income_quintiles")
    )
    table_title_income_quintiles_fr = charField(
        french=True, label=tm("table_title_income_quintiles_french")
    )

    # TREND
    title_trend = charField(label=tm("title_trend"))
    title_trend_fr = charField(french=True, label=tm("title_trend_french"))

    table_title_trend = charField(label=tm("table_title_trend"))
    table_title_trend_fr = charField(
        french=True, label=tm("table_title_trend_french")
    )

    visual_description_trend = charField(label=tm("visual_description_trend"))
    visual_description_trend_fr = charField(
        french=True, label=tm("visual_description_trend_french")
    )

    x_axis_trend = charField(label=tm("x_axis_trend"))
    x_axis_trend_fr = charField(french=True, label=tm("x_axis_trend_french"))

    y_axis_trend = charField(label=tm("y_axis_trend"))
    y_axis_trend_fr = charField(french=True, label=tm("y_axis_trend_french"))

    y_axis_trend_min = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    y_axis_trend_max = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    trend_footnotes = ckEditorField(label=tm("trend_footnotes"))
    trend_footnotes_fr = ckEditorField(
        french=True, label=tm("trend_footnotes_french")
    )

    # BENCHMARKING
    title_benchmark = charField(label=tm("title_benchmark"))
    title_benchmark_fr = charField(
        french=True, label=tm("title_benchmark_french")
    )

    table_title_benchmark = charField(label=tm("table_title_benchmark"))
    table_title_benchmark_fr = charField(
        french=True, label=tm("table_title_benchmark_french")
    )

    x_axis_benchmark = charField(label=tm("x_axis_benchmark"))
    x_axis_benchmark_fr = charField(
        french=True, label=tm("x_axis_benchmark_french")
    )

    benchmarking_dynamic_text = charField(
        label=tm("benchmarking_dynamic_text")
    )
    benchmarking_dynamic_text_fr = charField(
        french=True, label=tm("benchmarking_dynamic_text_french")
    )

    benchmarking_footnotes = ckEditorField(label=tm("benchmarking_footnotes"))
    benchmarking_footnotes_fr = ckEditorField(
        french=True, label=tm("benchmarking_footnotes_french")
    )

    benchmarking_sources_english = ckEditorField(
        label=tm("benchmarking_sources_english")
    )
    benchmarking_sources_fr = ckEditorField(
        french=True, label=tm("benchmarking_sources_french")
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

        sorted_all_shown_periods = sorted(
            all_shown_periods, key=lambda p: ((-p.year), (p.quarter or -1))
        )

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
            "sorted_all_shown_periods": sorted_all_shown_periods,
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
        data = group_by(
            list(self.indicator_data), lambda d: d.dimension_type_id
        )
        age_group_dim_id = DimensionType.objects.get(code="age").id
        age_data = data.get(age_group_dim_id, [])
        age_data = age_group_sort(age_data)
        data[age_group_dim_id] = age_data
        return data

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
