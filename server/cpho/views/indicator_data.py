from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm, inlineformset_factory
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
)
from cpho.text import tdt, tm

from .view_util import SinglePeriodMixin


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
        ]

    value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tdt("Value")}
        ),
    )
    value_lower_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tdt("Lower Bound")}
        ),
    )
    value_upper_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tdt("Upper Bound")}
        ),
    )
    data_quality = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.DATA_QUALITY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    value_unit = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.VALUE_UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    single_year_timeframe = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    multi_year_timeframe = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    literal_dimension_val = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def clean(self):
        cleaned_data = super().clean()
        value = cleaned_data["value"]
        value_unit = cleaned_data["value_unit"]
        if value_unit == "%":
            if value and (value > 100 or value < 0):
                self.add_error(
                    "value", tdt("Value must be a percentage between 0-100")
                )
        return cleaned_data

    def clean_value(self):
        value = self.cleaned_data["value"]
        if value and value < 0:
            print("invalid")
            self.add_error("value", tdt("Value cannot be negative"))
        return value

    def clean_value_lower_bound(self):
        value = self.cleaned_data["value"]
        value_lower = self.cleaned_data["value_lower_bound"]
        if (value and value_lower) and value < value_lower:
            self.add_error(
                "value_lower_bound",
                tdt("Value lower bound must be lower than value"),
            )
        return value_lower

    def clean_value_upper_bound(self):
        value = self.cleaned_data["value"]
        value_upper = self.cleaned_data["value_upper_bound"]
        if (value and value_upper) and value > value_upper:
            self.add_error(
                "value_upper_bound",
                tdt("Value upper bound must be greater than value"),
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
                        tdt(
                            "Single Year Timeframe must be between the years 2000 and 2050"
                        ),
                    )
            except ValueError:
                self.add_error(
                    "single_year_timeframe",
                    tdt("Single Year Timeframe must be a valid number"),
                )

        return single_year

    def clean_multi_year_timeframe(self):
        multi_year = self.cleaned_data["multi_year_timeframe"]

        if multi_year is None or multi_year == "":
            return None

        if multi_year:
            try:
                start_year, end_year = map(int, multi_year.split("-"))
                if not (2000 <= start_year <= end_year <= 2050):
                    self.add_error(
                        "multi_year_timeframe",
                        tdt(
                            "Multi Year Timeframe must be between the years 2000 and 2050 and start year must be less than end year"
                        ),
                    )
            except ValueError:
                self.add_error(
                    "multi_year_timeframe",
                    tdt(
                        "Multiyear timeframe must be in the form: 'YYYY-YYYY'"
                    ),
                )

        return multi_year


class ManageIndicatorData(SinglePeriodMixin, TemplateView):
    template_name = "indicator_data/manage_indicator_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    @cached_property
    def dimension_type(self):
        if "dimension_type_id" not in self.kwargs:
            return None

        return DimensionType.objects.prefetch_related("possible_values").get(
            id=self.kwargs["dimension_type_id"]
        )

    @cached_property
    def age_group_formset(self):
        existing_data = IndicatorDatum.objects.filter(
            indicator=self.indicator,
            dimension_type__code="age",
            period=self.period,
        ).order_by("dimension_value__order")

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            IndicatorDatum,
            fk_name="indicator",
            form=IndicatorDatumForm,
            # formset=ProjectOptionFormset,# TODO: use custom formset to validate groups are unique, contiguous, etc.
            extra=1,
            can_delete=True,
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

        return fs

    @cached_property
    def predefined_values_formset(self):
        # TODO: filter by period

        # getting all indicator data for this indicator
        existing_data = IndicatorDatum.objects.filter(
            indicator=self.indicator,
            dimension_type__is_literal=False,
            period=self.period,
        ).order_by("dimension_value__order")

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

        possible_values = DimensionValue.objects.filter(
            dimension_type__is_literal=False
        )
        if self.dimension_type is not None:
            possible_values = possible_values.filter(
                dimension_type=self.dimension_type
            )

        instances = []
        for pv in possible_values:
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
            form=IndicatorDatumForm, formset=InstanceProvidingFormSet, extra=0
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

    @cached_property
    def possible_values_by_dimension_type(self):
        return {
            dt: dt.possible_values.all()
            for dt in DimensionType.objects.all()
            .prefetch_related("possible_values")
            .filter(is_literal=False)
        }

    def post(self, *args, **kwargs):
        predefined_valid = self.predefined_values_formset.is_valid()
        age_group_valid = self.age_group_formset.is_valid()
        if predefined_valid and age_group_valid:
            with transaction.atomic():
                for form in self.predefined_values_formset:
                    form.save()

                self.age_group_formset.save()

                messages.success(
                    self.request, tdt("Data saved."), messages.SUCCESS
                )
                return redirect(
                    "view_indicator",
                    pk=self.indicator.pk,
                )
        else:
            # get will just render the forms and their errors
            # import IPython
            # IPython.embed()

            return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.dimension_type is None:
            predefined_dimension_types = DimensionType.objects.filter(
                is_literal=False
            )
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
        }

        return ctx
