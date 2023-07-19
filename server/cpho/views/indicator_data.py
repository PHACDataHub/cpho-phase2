from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm, inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
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
            "hso_approved",
            "program_approved",
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

    def save_changes(self):
        """
        Save form only if it has changed, otherwise do nothing.
        Implementing as a form function so upload can use it too(in the future)
        Bonus: This will prevent creating multiple history/version records
        """
        if self.has_changed():
            print("changed")
            print(self.changed_data)
            if "DELETE" in self.changed_data:
                if self.instance.id is not None:
                    self.instance.delete()
            elif self.changed_data in [
                ["program_approved"],
                ["hso_approved"],
                ["program_approved", "hso_approved"],
            ]:
                self.save()
            else:
                obj = self.save(commit=False)
                obj.program_approved = False
                obj.hso_approved = False
                obj.save()

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

    def action_type(self):
        return self.kwargs["action"]

    def form_type(self):
        if self.action_type() == "review" or self.action_type() == "view":
            return ReadOnlyIndicatorDatumForm
        elif self.action_type() == "edit":
            return IndicatorDatumForm

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
            form=self.form_type(),
            # formset=ProjectOptionFormset,# TODO: use custom formset to validate groups are unique, contiguous, etc.
            extra=1 if self.action_type() == "edit" else 0,
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
            form.instance.period = self.period

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
            form=self.form_type(),
            formset=InstanceProvidingFormSet,
            extra=0,
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
                    form.save_changes()

                for form in self.age_group_formset:
                    form.save_changes()

                # self.age_group_formset.save()

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

            print(
                "predefined_values_formset.errors",
                self.predefined_values_formset.errors,
            )
            print("age_group_formset.errors", self.age_group_formset.errors)
            for form in self.age_group_formset:
                print("form.value", form.instance.value)
                print("form.errors", form.errors)
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
            "dimension_type": "all"
            if self.dimension_type is None
            else self.dimension_type.code,
            "read_only": self.action_type() == "view"
            or self.action_type() == "review",
            "action_type": self.action_type(),
            "period": self.period,
        }

        return ctx


class ReadOnlyFormMixin:
    """A form mixin for the read only view that includes methods to
    disable fields and remove placeholders."""

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFormMixin, self).__init__(*args, **kwargs)

    def disable_fields(self):
        """Disable all fields in the form."""
        for field in self.fields:
            # print(field)
            if field not in ["hso_approved", "program_approved"]:
                self.fields[field].widget.attrs["disabled"] = True

    def remove_placeholders(self):
        """Remove all placeholders from the form."""
        for field in self.fields:
            self.fields[field].widget.attrs.pop("placeholder", None)


class ReadOnlyIndicatorDatumForm(IndicatorDatumForm, ReadOnlyFormMixin):
    def __init__(self, *args, **kwargs):
        super(IndicatorDatumForm, self).__init__(*args, **kwargs)
        self.disable_fields()
        self.remove_placeholders()


# class ApproveIndicatorData(TemplateView):
#     def indicator(self):
#         return Indicator.objects.get(pk=self.kwargs["indicator_id"])

#     def period(self):
#         return Period.objects.get(pk=self.kwargs["period_id"])

#     def post(self, *args, **kwargs):
#         response = HttpResponse()

#         relevant_data = IndicatorDatum.objects.filter(
#             indicator=self.indicator(), period=self.period()
#         )
#         for data in relevant_data:
#             data.hso_approved = True
#             data.program_approved = True
#             data.save()
#         # print(dir(data.versions.create))
#         # data.versions.latest().hso_approved = True
#         # data.save()
#         # data.versions.create(hso_approved=True)
#         # print(data.versions.latest().hso_approved)
#         # print(dir(data.versions))

#         response["HX-Redirect"] = reverse(
#             "view_indicator", kwargs={"pk": self.indicator().pk}
#         )
#         return response
