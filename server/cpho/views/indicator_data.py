from django import forms
from django.contrib import messages
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm
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
        ]

    value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Value"}
        ),
    )
    value_lower_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Lower Bound"}
        ),
    )
    value_upper_bound = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Upper Bound"}
        ),
    )
    data_quality = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.DATA_QUALITY_CHOICES,
        # label="Data Quality",
        # initial="caution",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    value_unit = forms.ChoiceField(
        required=False,
        choices=IndicatorDatum.VALUE_UNIT_CHOICES,
        # label="Data Quality",
        # initial="caution",
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


class ManageIndicatorData(TemplateView):
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
    def formset(self):
        # TODO: filter by period
        existing_data = IndicatorDatum.objects.filter(
            indicator=self.indicator,
        ).order_by("dimension_value__order")
        if self.dimension_type is not None:
            existing_data = existing_data.filter(
                indicator=self.indicator,
                dimension_value__dimension_type=self.dimension_type,
            )

        existing_data_by_dimension_value = {
            datum.dimension_value: datum for datum in existing_data
        }

        possible_values = DimensionValue.objects.all()
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
                    indicator=self.indicator, dimension_value=pv
                )
            instances.append(record)

        factory = formset_factory(
            form=IndicatorDatumForm, formset=InstanceProvidingFormSet, extra=0
        )
        formset_kwargs = {
            "initial": [{} for x in possible_values],
            "instances": instances,
        }
        if self.request.POST:
            formset = factory(self.request.POST, **formset_kwargs)
        else:
            formset = factory(**formset_kwargs)

        return formset

    @cached_property
    def forms_by_dimension_value(self):
        return {
            form.instance.dimension_value: form for form in self.formset.forms
        }

    @cached_property
    def possible_values_by_dimension_type(self):
        return {
            dt: dt.possible_values.all()
            for dt in DimensionType.objects.all().prefetch_related(
                "possible_values"
            )
        }

    def post(self, *args, **kwargs):
        print("entered post")
        if self.formset.is_valid():
            print("formset is valid")
            with transaction.atomic():
                for form in self.formset:
                    form.save()

                messages.success(
                    self.request, tdt("Data saved."), messages.SUCCESS
                )
                return redirect(
                    "view_indicator",
                    pk=self.indicator.pk,
                )
        else:
            print("formset is not valid")
            for form in self.formset:
                print(form.errors)
            print(self.formset.errors)
            messages.error(self.request, tdt("Please correct the errors."))

    def get_context_data(self, **kwargs):
        if self.dimension_type is None:
            dimension_types = DimensionType.objects.all()
        else:
            dimension_types = [self.dimension_type]

        return {
            **super().get_context_data(**kwargs),
            "indicator": self.indicator,
            "dimension_types": dimension_types,
            "formset": self.formset,
            "forms_by_dimension_value": self.forms_by_dimension_value,
            "possible_values_by_dimension_type": self.possible_values_by_dimension_type,
        }
