import re

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.forms import BaseInlineFormSet
from django.utils.functional import cached_property
from django.views.generic import TemplateView, View

from phac_aspc.rules import test_rule

from cpho.models import DimensionType, DimensionValue, Period
from cpho.text import tdt, tm


class ReadOnlyFormMixin:
    """A form mixin for the read only view that includes methods to
    disable fields and remove placeholders."""

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFormMixin, self).__init__(*args, **kwargs)

    def disable_fields(self):
        """Disable all fields in the form."""
        for field in self.fields:
            self.fields[field].widget.attrs["disabled"] = True

    def remove_placeholders(self):
        """Remove all placeholders from the form."""
        for field in self.fields:
            self.fields[field].widget.attrs.pop("placeholder", None)

    def choice_to_text_field(self):
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ChoiceField):
                value_to_display = dict(field.choices).get(
                    self.initial.get(field_name)
                )
                self.fields[field_name].widget = forms.TextInput(
                    attrs={
                        "class": "form-control",
                    },
                )
                self.initial[field_name] = value_to_display


class RequiredIfNotDeletedMixin:
    def clean(self):
        super().clean()
        if self.REQUIRED_UNLESS_DELETED:
            is_deleted = self.cleaned_data.get("is_deleted")
            for field_name in self.REQUIRED_UNLESS_DELETED:
                field_value = self.cleaned_data.get(field_name, None)
                print(field_name, field_value, not (field_value))
                if not is_deleted and not field_value:
                    self.add_error(
                        field_name, tm("required_if_not_deleted_err")
                    )
        return self.cleaned_data


class BaseInlineFormSetWithUniqueTogetherCheck(BaseInlineFormSet):
    def clean(
        self,
        fields=None,
    ):
        super().clean()
        if self.model._meta.unique_together or fields:
            unique_combinations = (set(fields) if fields else None) or set(
                self.model._meta.unique_together
            )
            if unique_combinations:
                values = {}
                for idx, unique_tuple in enumerate(unique_combinations):
                    values[idx] = set()
                for form in self.forms:
                    if not hasattr(form, "cleaned_data"):
                        continue
                    if not any(form.cleaned_data.values()):
                        continue
                    form_is_dupe = []
                    for idx, unique_tuple in enumerate(unique_combinations):
                        if form.cleaned_data != {}:
                            value = tuple(
                                form.cleaned_data.get(field)
                                for field in unique_tuple
                                if form.cleaned_data.get(field) is not None
                            )
                            if value in values[idx]:
                                form_is_dupe.append(True)
                            else:
                                form_is_dupe.append(False)
                            values[idx].add(value)

                    if all(form_is_dupe):
                        common_fields = set()
                        if len(unique_combinations) > 1:
                            common_fields = set.intersection(
                                *map(set, unique_combinations)
                            )
                        fields_to_change = []
                        for unique_tuple in unique_combinations:
                            for field in unique_tuple:
                                if (
                                    field
                                    not in [
                                        *list(common_fields),
                                        "is_deleted",
                                        "deletion_time",
                                        "indicator",
                                    ]
                                    and field in form.fields
                                ):
                                    fields_to_change.append(field)
                        error_msg = tm("formset_dupe_msg")
                        for field in fields_to_change:
                            field_name = None
                            field_value = None
                            if field == "literal_dimension_val":
                                field_name = form.instance.dimension_type.name
                            else:
                                field_name = form.fields[field].label
                            if hasattr(form.fields[field], "_choices"):
                                val = form.cleaned_data.get(field)
                                field_value = dict(
                                    form.fields[field].choices
                                ).get(val)
                            else:
                                field_value = form.cleaned_data.get(field)

                            error_msg += f"{field_name}: {field_value}, "
                        error_msg = error_msg[:-2]

                        form.add_error(None, tm("duplicate_form"))

                        raise ValidationError(error_msg)


class IndDataCleaner:
    """
    Mixin for cleaning indicator data values
    Shared data validation logic between the indicator data form and the indicator data upload.
    """

    @staticmethod
    def clean_value_data(value, value_unit):
        if value:
            value = float(value)
            if value < 0:
                return tm("value_cannot_be_negative")
            if value_unit == "percentage":
                if value and (value > 100 or value < 0):
                    return tm("percentage_out_of_bounds_err")
        return None

    @staticmethod
    def clean_value_lower_data(value, value_lower):
        if (value and value_lower) and float(value) < float(value_lower):
            return tm("lower_bound_must_be_lower_than_value")
        return None

    @staticmethod
    def clean_value_upper_data(value, value_upper):
        if (value and value_upper) and float(value) > float(value_upper):
            return tm("upper_bound_must_be_greater_than_value")
        return None

    @staticmethod
    def clean_single_year_data(single_year):
        if single_year is None or single_year == "":
            return None
        if single_year:
            try:
                if not (int(single_year) >= 2000 and int(single_year) <= 2050):
                    return tm("year_timeframe_between")
            except Exception:
                return tm("must_be_number")
        return None

    @staticmethod
    def clean_multi_year_data(multi_year):
        if multi_year is None or multi_year == "":
            return None
        if multi_year:
            try:
                start_year = int(multi_year.split("-")[0])
                end_year = int(multi_year.split("-")[1])
                if not (2000 <= start_year <= end_year <= 2050):
                    return tm("year_timeframe_between")
            except Exception:
                return tm("multi_year_format")
        return None


class SinglePeriodMixin(View):
    """
    note: this mixin needs to be to the left of generic views in order for the context to include 'period'
    assumes the URL has a period_pk kwarg
    """

    def get_period_id(self):
        return self.kwargs["period_pk"]

    @cached_property
    def period(self):
        return Period.objects.get(pk=self.get_period_id())

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
            "period": self.period,
        }


class DimensionTypeOrAllMixin(View):
    """
    Several views have a dimension_type_id kwarg that is NULL
    when we want all dimensions covered
    """

    @cached_property
    def dimension_type(self):
        if "dimension_type_id" not in self.kwargs:
            return None

        return DimensionType.objects.prefetch_related("possible_values").get(
            id=self.kwargs["dimension_type_id"]
        )


class MustPassAuthCheckMixin(View):
    def check_rule(self):
        raise NotImplementedError("must override check_rule")

    def dispatch(self, request, *args, **kwargs):
        if not self.check_rule():
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class MustBeAdminOrHsoMixin(MustPassAuthCheckMixin):
    def check_rule(self):
        return test_rule("is_admin_or_hso", self.request.user)


def age_group_sortable_score(indicator_datum):
    match = re.findall(
        r"[<]?\d+[+]?", indicator_datum.literal_dimension_val.lower()
    )
    if match:
        first_numeric = match[0]
        if "<" in first_numeric:
            return str(int(first_numeric.replace("<", "").strip()) - 1).zfill(
                6
            )
        if "+" in first_numeric:
            return str(int(first_numeric.replace("+", "").strip()) + 1).zfill(
                6
            )
        else:
            return str(int(first_numeric.replace("+", "").strip())).zfill(6)
    return indicator_datum.literal_dimension_val.lower()


def age_group_sort(qs):
    return sorted(qs, key=age_group_sortable_score)


def metadata_mapper():
    all_dimensions = DimensionType.objects.all()
    all_dimension_dict = {
        dimension.code: dimension for dimension in all_dimensions
    }
    all_dimension_vals = DimensionValue.objects.all()
    all_dimension_val_dict = {
        dimension_val.value: dimension_val
        for dimension_val in all_dimension_vals
    }
    all_period_dict = {period.code: period for period in Period.objects.all()}
    return {
        "comparison_mapper": {
            "": "",
            "similar": "Similar",
            "better": "Better",
            "worse": "Worse",
            "outlier": "Outlier",
        },
        "labels_mapper": {
            "": "",
            "anxiety": "Anxiety",
            "depression": "Depression",
            "women": "Women",
            "men": "Men",
        },
        "unit_mapper": {
            "": "",
            "AGE-STANDARDIZED RATE": "age_rate",
            "CRUDE RATE": "crude_rate",
            "DEFINED DAILY DOSE/1,000 CENSUS INHABITANTS": "daily_dose_per_1k_census",
            "PERCENTAGE": "percentage",
            "PERCENTAGE (CRUDE RATE)": "percentage_crude_rate",
            "RATE PER 10,000 PATIENT DAYS": "rate_per_10k_patient",
            "RATE PER 100,000": "rate_per_100k",
            "RATE PER 100,000 (CRUDE RATE)": "rate_per_100k_crude",
            "RATE PER 100,000 LIVE BIRTHS": "rate_per_100k_live_births",
            "YEARS": "years",
            "LITRES PER PERSON": "litres_per_person",
            "OTHER": "other",
        },
        "value_displayed_mapper": {
            "": "",
            "%": "%",
            "PER 100,000": "per_100k",
            "YEARS": "years",
            "PER 1,000 CENSUS INHABITANTS": "per_1k_census",
            "PER 10,000 PATIENT DAYS": "per_10k_patient",
            "PER 100,000 LIVE BIRTHS": "per_100k_live_births",
            "OTHER": "other",
        },
    }
