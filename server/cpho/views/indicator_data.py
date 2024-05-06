from datetime import datetime

from django import forms
from django.contrib import messages
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm
from django.forms.utils import ErrorDict
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from phac_aspc.rules import test_rule

from cpho.constants import SUBMISSION_STATUSES
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
)
from cpho.queries import relevant_dimension_types_for_period
from cpho.text import tdt, tm
from cpho.views.view_util import (
    BaseInlineFormSetWithUniqueTogetherCheck,
    DimensionTypeOrAllMixin,
    MustPassAuthCheckMixin,
    ReadOnlyFormMixin,
    SinglePeriodMixin,
)


class InstanceProvidingFormSet(BaseFormSet):
    """
    model formsets are tied to querysets. A queryset can't contain blank records
    so we use a custom formset and explicitely provide instances (some saved, some not)
    """

    def __init__(self, *args, instances=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.instances = instances

    def get_form_kwargs(self, index):
        return {
            **super().get_form_kwargs(index),
            "instance": self.instances[index],
        }


class IndicatorDatumForm(ModelForm):
    class Meta:
        model = IndicatorDatum
        fields = [
            "value",
            "data_quality",
            "value_lower_bound",
            "value_upper_bound",
            "value_unit",
            "single_year_timeframe",
            "multi_year_timeframe",
            "literal_dimension_val",
            "value_displayed",
            "reason_for_null",
            "is_deleted",
            "deletion_time",
        ]

    value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tm("value")}
        ),
        label=tm("value"),
    )
    value_lower_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tm("lower_bound")}
        ),
        label=tm("lower_bound"),
    )
    value_upper_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tm("upper_bound")}
        ),
        label=tm("upper_bound"),
    )
    data_quality = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.DATA_QUALITY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("data_quality"),
    )
    value_unit = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.VALUE_UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("value_unit"),
    )
    single_year_timeframe = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("single_year_timeframe"),
    )
    multi_year_timeframe = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("multi_year_timeframe"),
    )
    literal_dimension_val = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("literal_dimension_value"),
    )
    value_displayed = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.VALUE_DISPLAYED_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("value_displayed"),
    )
    reason_for_null = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.REASON_FOR_NULL_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("reason_for_null_data"),
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

    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, "cleaned_data") and self.cleaned_data["is_deleted"]:
            self._errors = ErrorDict()
            return self.cleaned_data
        value = cleaned_data["value"]
        value_unit = cleaned_data["value_unit"]
        if value_unit == "%":
            if value and (value > 100 or value < 0):
                self.add_error(
                    "value",
                    tm("percentage_out_of_bounds_err"),
                )
        return cleaned_data

    def clean_value(self):
        value = self.cleaned_data["value"]
        if value and value < 0:
            print("invalid")
            self.add_error("value", tm("value_cannot_be_negative"))
        return value

    def clean_value_lower_bound(self):
        value = self.cleaned_data["value"]
        value_lower = self.cleaned_data["value_lower_bound"]
        if (value and value_lower) and value < value_lower:
            self.add_error(
                "value_lower_bound",
                tm("lower_bound_must_be_lower_than_value"),
            )
        return value_lower

    def clean_value_upper_bound(self):
        value = self.cleaned_data["value"]
        value_upper = self.cleaned_data["value_upper_bound"]
        if (value and value_upper) and value > value_upper:
            self.add_error(
                "value_upper_bound",
                tm("upper_bound_must_be_greater_than_value"),
            )
        return value_upper

    def clean_single_year_timeframe(self):
        single_year = self.cleaned_data["single_year_timeframe"]

        if single_year is None or single_year == "":
            return None

        if single_year:
            try:
                if not (int(single_year) >= 2000 and int(single_year) <= 2050):
                    self.add_error(
                        "single_year_timeframe",
                        tm("year_timeframe_between"),
                    )
            except ValueError:
                self.add_error(
                    "single_year_timeframe",
                    tm("must_be_number"),
                )

        return single_year

    def clean_multi_year_timeframe(self):
        multi_year = self.cleaned_data["multi_year_timeframe"]

        if multi_year is None or multi_year == "":
            return None

        if multi_year:
            try:
                start_year = int(multi_year.split("-")[0])
                end_year = int(multi_year.split("-")[1])
                if not (2000 <= start_year <= end_year <= 2050):
                    self.add_error(
                        "multi_year_timeframe",
                        tm("year_timeframe_between"),
                    )
            except ValueError:
                self.add_error(
                    "multi_year_timeframe",
                    tm("multi_year_format"),
                )

        return multi_year

    def save(self, commit=True):
        if self.cleaned_data["is_deleted"]:
            self.instance.deletion_time = str(datetime.now())
        return super().save(commit)


class ReadOnlyIndicatorDatumForm(IndicatorDatumForm, ReadOnlyFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice_to_text_field()
        self.disable_fields()
        self.remove_placeholders()


class ManageIndicatorData(
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
    DimensionTypeOrAllMixin,
    TemplateView,
):
    template_name = "indicator_data/manage_indicator_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    @cached_property
    def form_type(self):
        if test_rule(
            "can_edit_indicator_data",
            self.request.user,
            {"indicator": self.indicator, "period": self.period},
        ):
            return IndicatorDatumForm
        return ReadOnlyIndicatorDatumForm

    @cached_property
    def age_group_formset(self):
        existing_data = (
            IndicatorDatum.active_objects.filter(
                indicator=self.indicator,
                dimension_type__code="age",
                period=self.period,
            )
            .order_by("dimension_value__order")
            .with_submission_annotations()
        )

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            IndicatorDatum,
            fk_name="indicator",
            form=self.form_type,
            # formset=ProjectOptionFormset,# TODO: use custom formset to validate groups are unique, contiguous, etc.
            formset=BaseInlineFormSetWithUniqueTogetherCheck,
            extra=1 if self.form_type == IndicatorDatumForm else 0,
            can_delete=False,
        )

        kwargs = {
            "queryset": existing_data,
            "instance": self.indicator,
            "prefix": "agegroup",
        }
        if self.request.POST:
            fs = InlineFormsetCls(self.request.POST, **kwargs)
        else:
            fs = InlineFormsetCls(**kwargs)

        age_dimension = DimensionType.objects.get(code="age")
        for form in fs:
            # new unsaved instances' save() crash when no dimension type is specified
            form.instance.dimension_type = age_dimension
            form.instance.period = self.period

        return fs

    @cached_property
    def predefined_values_formset(self):
        # TODO: filter by period

        # getting all indicator data for this indicator
        existing_data = (
            IndicatorDatum.active_objects.filter(
                indicator=self.indicator,
                dimension_type__is_literal=False,
                period=self.period,
            )
            .order_by("dimension_value__order")
            .with_submission_annotations()
        )

        # value for all not selected only get data for stratifier selected
        if self.dimension_type is not None:
            existing_data = existing_data.filter(
                dimension_type=self.dimension_type.id,
            )

        existing_data_by_dimension_value = {
            datum.dimension_value: datum
            for datum in existing_data.filter(
                literal_dimension_val__isnull=True
            )
        }
        # looks like {"Male": <male data>, "Canada": <Canada data> }

        possible_values = DimensionValue.objects.filter(
            dimension_type__is_literal=False
        )
        # looks like [<Male dim val>, <Female dim val>, <Canada dim val>...]
        if self.dimension_type is not None:
            possible_values = possible_values.filter(
                dimension_type=self.dimension_type
            )
        # if managing data for sex
        # looks like [<Male dim val>, <Female dim val>]

        instances = []
        for pv in possible_values:
            # get existing record for each dim val or create a new one and append to instances
            if existing_data_by_dimension_value.get(pv, None):
                record = existing_data_by_dimension_value[pv]
            else:
                record = IndicatorDatum(
                    indicator=self.indicator,
                    dimension_value=pv,
                    dimension_type_id=pv.dimension_type_id,
                    period=self.period,
                )
            instances.append(record)

        factory = formset_factory(
            form=self.form_type, formset=InstanceProvidingFormSet, extra=0
        )
        formset_kwargs = {
            "initial": [{} for x in possible_values],
            "instances": instances,
            "prefix": "predefined",
        }
        if self.request.POST:
            formset = factory(self.request.POST, **formset_kwargs)
        else:
            formset = factory(**formset_kwargs)

        return formset

    @cached_property
    def forms_by_dimension_value(self):
        return {
            form.instance.dimension_value: form
            for form in self.predefined_values_formset.forms
        }

    # looks like {"Male": <male form>, "Canada": <Canada form> }

    @cached_property
    def possible_values_by_dimension_type(self):
        return {
            dt: dt.possible_values.all()
            for dt in DimensionType.objects.all()
            .prefetch_related("possible_values")
            .filter(is_literal=False)
        }

    @cached_property
    def has_age_group_forms(self):
        if self.dimension_type is None:
            # if age not in relevant dimensions for indicator, but age data exists for this period
            for dt in relevant_dimension_types_for_period(
                self.indicator, self.period
            ):
                if dt.code == "age":
                    return True
        elif self.dimension_type.code == "age":
            return True
        return False

    def check_rule(self):
        return test_rule(
            "can_view_indicator_data", self.request.user, self.indicator
        )

    def post(self, *args, **kwargs):
        predefined_valid = self.predefined_values_formset.is_valid()
        age_group_valid = (
            not self.has_age_group_forms or self.age_group_formset.is_valid()
        )
        if predefined_valid and age_group_valid:
            with transaction.atomic():
                for form in self.predefined_values_formset:
                    if form.has_changed():
                        form.save()

                if self.has_age_group_forms:
                    self.age_group_formset.save()

                messages.success(self.request, tm("saved_successfully"))
                return redirect(
                    reverse(
                        "view_indicator_for_period",
                        args=[self.indicator.pk, self.period.id],
                    ),
                )
        else:
            # get will just render the forms and their errors
            print(self.predefined_values_formset.errors)
            print(self.age_group_formset.errors)
            messages.error(self.request, tm("error_saving_form"))
            return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.dimension_type is None:
            predefined_dimension_types = DimensionType.objects.filter(
                is_literal=False,
                code__in=[
                    dim.code
                    for dim in relevant_dimension_types_for_period(
                        self.indicator, self.period
                    )
                ],
            ).order_by("order")

        elif self.dimension_type.code == "age":
            predefined_dimension_types = []
        else:
            predefined_dimension_types = [self.dimension_type]

        ctx = {
            **super().get_context_data(**kwargs),
            "indicator": self.indicator,
            "predefined_dimension_types": predefined_dimension_types,
            "predefined_values_formset": self.predefined_values_formset,
            "forms_by_dimension_value": self.forms_by_dimension_value,
            "possible_values_by_dimension_type": self.possible_values_by_dimension_type,
            "age_group_formset": self.age_group_formset,
            "show_age_group": self.has_age_group_forms,
        }

        return ctx
