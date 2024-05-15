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


def upload_mapper():
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
        "category_mapper": {
            "": "",
            "FACTORS INFLUENCING HEALTH": "factors_influencing_health",
            "GENERAL HEALTH STATUS": "general_health_status",
            "HEALTH OUTCOMES": "health_outcomes",
        },
        "topic_mapper": {
            "": "",
            "SOCIAL FACTORS": "social_factors",
            "HEALTH STATUS": "health_status",
            "COMMUNICABLE DISEASES": "communicable_diseases",
            "SUBSTANCE USE": "substance_use",
            "CHILDHOOD AND FAMILY FACTORS": "childhood_and_family_factors",
            "CHRONIC DISEASES AND MENTAL HEALTH": "chronic_diseases_and_mental_health",
        },
        "data_quality_mapper": {
            "": "",
            "CAUTION": "caution",
            "GOOD": "good",
            "ACCEPTABLE": "acceptable",
            "SUPPRESSED": "suppressed",
            "VERY GOOD": "very good",
        },
        "reason_for_null_mapper": {
            "": "",
            "Suppressed": "suppressed",
            "Not available": "not_available",
        },
        "value_unit_mapper": {
            "": "",
            "DEFINED DAILY DOSE/1,000 CENSUS INHABITANTS": "daily_dose_1k_census",
            "PERCENTAGE": "percentage",
            "PERCENTAGE (AGE STANDARDIZED)": "percent_age_standardized",
            "PERCENTAGE (CRUDE)": "percentage_crude",
            "RATE PER 10,000 PATIENT DAYS": "rate_10k_patient_days",
            "RATE PER 100,000 (AGE-STANDARDIZED)": "rate_100k_age_standardized",
            "RATE PER 100,000 (AGE-SPECIFIC CRUDE)": "rate_100k_age_specific_crude",
            "RATE PER 100,000 (CRUDE)": "rate_100k_crude",
            "RATE PER 100,000 LIVE BIRTHS": "rate_100k_live_births",
            "RATE PER 100,000 POPULATION PER YEAR": "rate_100k_population_per_year",
            "YEARS": "years",
            "OTHER": "other",
        },
        "value_displayed_mapper": {
            "": "",
            "%": "%",
            "DDDs PER 1,000 CENSUS INHABITANTS": "per_1k_census",
            "PER 10,000 PATIENT DAYS": "per_10k_patient_days",
            "PER 100,000 LIVE BIRTHS": "per_100k_live_births",
            "PER 100,000 POPULATION": "per_100k_population",
            "PER 100,000 POPULATION PER YEAR": "per_100k_population_per_year",
            "YEARS": "years",
            "OTHER": "other",
        },
        "dimension_type_mapper": {
            "Province": all_dimension_dict["province"],
            "Age Group": all_dimension_dict["age"],
            "Sex": all_dimension_dict["sex"],
            "Canada": all_dimension_dict["canada"],
            "Region": all_dimension_dict["region"],
            "Gender": all_dimension_dict["gender"],
            "Living Arrangement": all_dimension_dict["living_arrangement"],
            "Education Household": all_dimension_dict["education_household"],
            "Income Quintiles": all_dimension_dict["income_quintiles"],
        },
        "period_mapper": all_period_dict,
        "non_literal_dimension_value_mapper": {
            ("Province", "ON"): all_dimension_val_dict["on"],
            ("Province", "AB"): all_dimension_val_dict["ab"],
            ("Province", "SK"): all_dimension_val_dict["sk"],
            ("Province", "MB"): all_dimension_val_dict["mb"],
            ("Province", "BC"): all_dimension_val_dict["bc"],
            ("Province", "QC"): all_dimension_val_dict["qc"],
            ("Province", "NB"): all_dimension_val_dict["nb"],
            ("Province", "NS"): all_dimension_val_dict["ns"],
            ("Province", "NL"): all_dimension_val_dict["nl"],
            ("Province", "PE"): all_dimension_val_dict["pe"],
            ("Province", "NU"): all_dimension_val_dict["nu"],
            ("Province", "NT"): all_dimension_val_dict["nt"],
            ("Province", "YT"): all_dimension_val_dict["yt"],
            ("Region", "ATLANTIC"): all_dimension_val_dict["atlantic"],
            ("Region", "PRAIRIE"): all_dimension_val_dict["prairies"],
            ("Region", "TERRITORIES"): all_dimension_val_dict["territories"],
            ("Gender", "MEN"): all_dimension_val_dict["men"],
            ("Gender", "WOMEN"): all_dimension_val_dict["women"],
            ("Gender", "BOYS"): all_dimension_val_dict["boys"],
            ("Gender", "GIRLS"): all_dimension_val_dict["girls"],
            ("Gender", "MEN+"): all_dimension_val_dict["men_plus"],
            ("Gender", "WOMEN+"): all_dimension_val_dict["women_plus"],
            ("Sex", "MALES"): all_dimension_val_dict["m"],
            ("Sex", "FEMALES"): all_dimension_val_dict["f"],
            ("Canada", "CANADA"): all_dimension_val_dict["canada"],
            (
                "Living Arrangement",
                "MALES LIVING ALONE",
            ): all_dimension_val_dict["male_alone"],
            (
                "Living Arrangement",
                "MALES IN SINGLE-PARENT FAMILY",
            ): all_dimension_val_dict["male_single_parent_family"],
            (
                "Living Arrangement",
                "MALES LIVING WITH OTHERS OR OTHER ARRANGEMENTS",
            ): all_dimension_val_dict["male_other"],
            (
                "Living Arrangement",
                "MALES COUPLE WITH CHILDREN",
            ): all_dimension_val_dict["male_couple_with_children"],
            (
                "Living Arrangement",
                "MALES COUPLE WITHOUT CHILDREN",
            ): all_dimension_val_dict["male_couple_no_children"],
            (
                "Living Arrangement",
                "FEMALES LIVING ALONE",
            ): all_dimension_val_dict["female_alone"],
            (
                "Living Arrangement",
                "FEMALES IN SINGLE-PARENT FAMILY",
            ): all_dimension_val_dict["female_single_parent_family"],
            (
                "Living Arrangement",
                "FEMALES LIVING WITH OTHERS OR OTHER ARRANGEMENTS",
            ): all_dimension_val_dict["female_other"],
            (
                "Living Arrangement",
                "FEMALES COUPLE WITH CHILDREN",
            ): all_dimension_val_dict["female_couple_with_children"],
            (
                "Living Arrangement",
                "FEMALES COUPLE WITHOUT CHILDREN",
            ): all_dimension_val_dict["female_couple_no_children"],
            (
                "Living Arrangement",
                "BOTH SEXES LIVING ALONE",
            ): all_dimension_val_dict["both_alone"],
            (
                "Living Arrangement",
                "BOTH SEXES IN SINGLE-PARENT FAMILY",
            ): all_dimension_val_dict["both_single_parent_family"],
            (
                "Living Arrangement",
                "BOTH SEXES LIVING WITH OTHERS OR OTHER ARRANGEMENTS",
            ): all_dimension_val_dict["both_other"],
            (
                "Living Arrangement",
                "BOTH SEXES COUPLE WITH CHILDREN",
            ): all_dimension_val_dict["both_couple_with_children"],
            (
                "Living Arrangement",
                "BOTH SEXES COUPLE WITHOUT CHILDREN",
            ): all_dimension_val_dict["both_couple_no_children"],
            (
                "Education Household",
                "MALES Less than high school",
            ): all_dimension_val_dict["males_less_than_high_school"],
            (
                "Education Household",
                "MALES High school graduate",
            ): all_dimension_val_dict["males_high_school_graduate"],
            (
                "Education Household",
                "MALES Community college/ Technical school/ University certificate",
            ): all_dimension_val_dict["males_certificate"],
            (
                "Education Household",
                "MALES University graduate",
            ): all_dimension_val_dict["males_university_graduate"],
            (
                "Education Household",
                "MALES Missing",
            ): all_dimension_val_dict["males_education_missing"],
            (
                "Education Household",
                "FEMALES Less than high school",
            ): all_dimension_val_dict["females_less_than_high_school"],
            (
                "Education Household",
                "FEMALES High school graduate",
            ): all_dimension_val_dict["females_high_school_graduate"],
            (
                "Education Household",
                "FEMALES Community college/ Technical school/ University certificate",
            ): all_dimension_val_dict["females_certificate"],
            (
                "Education Household",
                "FEMALES University graduate",
            ): all_dimension_val_dict["females_university_graduate"],
            (
                "Education Household",
                "FEMALES Missing",
            ): all_dimension_val_dict["females_education_missing"],
            (
                "Education Household",
                "BOTH SEXES Less than high school",
            ): all_dimension_val_dict["both_less_than_high_school"],
            (
                "Education Household",
                "BOTH SEXES High school graduate",
            ): all_dimension_val_dict["both_high_school_graduate"],
            (
                "Education Household",
                "BOTH SEXES Community college/ Technical school/ University certificate",
            ): all_dimension_val_dict["both_certificate"],
            (
                "Education Household",
                "BOTH SEXES University graduate",
            ): all_dimension_val_dict["both_university_graduate"],
            (
                "Education Household",
                "BOTH SEXES Missing",
            ): all_dimension_val_dict["both_education_missing"],
            (
                "Income Quintiles",
                "MALES Quintile 1",
            ): all_dimension_val_dict["male_quintile_1"],
            (
                "Income Quintiles",
                "MALES Quintile 2",
            ): all_dimension_val_dict["male_quintile_2"],
            (
                "Income Quintiles",
                "MALES Quintile 3",
            ): all_dimension_val_dict["male_quintile_3"],
            (
                "Income Quintiles",
                "MALES Quintile 4",
            ): all_dimension_val_dict["male_quintile_4"],
            (
                "Income Quintiles",
                "MALES Quintile 5",
            ): all_dimension_val_dict["male_quintile_5"],
            (
                "Income Quintiles",
                "MALES Missing",
            ): all_dimension_val_dict["male_quintile_missing"],
            (
                "Income Quintiles",
                "FEMALES Quintile 1",
            ): all_dimension_val_dict["female_quintile_1"],
            (
                "Income Quintiles",
                "FEMALES Quintile 2",
            ): all_dimension_val_dict["female_quintile_2"],
            (
                "Income Quintiles",
                "FEMALES Quintile 3",
            ): all_dimension_val_dict["female_quintile_3"],
            (
                "Income Quintiles",
                "FEMALES Quintile 4",
            ): all_dimension_val_dict["female_quintile_4"],
            (
                "Income Quintiles",
                "FEMALES Quintile 5",
            ): all_dimension_val_dict["female_quintile_5"],
            (
                "Income Quintiles",
                "FEMALES Missing",
            ): all_dimension_val_dict["female_quintile_missing"],
            (
                "Income Quintiles",
                "BOTH SEXES Quintile 1",
            ): all_dimension_val_dict["both_quintile_1"],
            (
                "Income Quintiles",
                "BOTH SEXES Quintile 2",
            ): all_dimension_val_dict["both_quintile_2"],
            (
                "Income Quintiles",
                "BOTH SEXES Quintile 3",
            ): all_dimension_val_dict["both_quintile_3"],
            (
                "Income Quintiles",
                "BOTH SEXES Quintile 4",
            ): all_dimension_val_dict["both_quintile_4"],
            (
                "Income Quintiles",
                "BOTH SEXES Quintile 5",
            ): all_dimension_val_dict["both_quintile_5"],
            (
                "Income Quintiles",
                "BOTH SEXES Missing",
            ): all_dimension_val_dict["both_quintile_missing"],
        },
    }


def export_mapper():
    all_dimension_vals = DimensionValue.objects.all()
    all_dimension_val_dict = {
        dimension_val.value: dimension_val
        for dimension_val in all_dimension_vals
    }

    upload_mapping = upload_mapper()

    export_mapping = {
        "category_mapper": {
            v: k for k, v in upload_mapping["category_mapper"].items()
        },
        "topic_mapper": {
            v: k for k, v in upload_mapping["topic_mapper"].items()
        },
        "data_quality_mapper": {
            v: k for k, v in upload_mapping["data_quality_mapper"].items()
        },
        "reason_for_null_mapper": {
            v: k for k, v in upload_mapping["reason_for_null_mapper"].items()
        },
        "value_unit_mapper": {
            v: k for k, v in upload_mapping["value_unit_mapper"].items()
        },
        "value_displayed_mapper": {
            v: k for k, v in upload_mapping["value_displayed_mapper"].items()
        },
        "dimension_type_mapper": {
            v: k for k, v in upload_mapping["dimension_type_mapper"].items()
        },
        "non_literal_dimension_value_mapper": {
            v: k[1]
            for k, v in upload_mapping[
                "non_literal_dimension_value_mapper"
            ].items()
        },
        # "non_literal_dimension_value_mapper": {
        #     all_dimension_val_dict["on"]: "ON",
        #     all_dimension_val_dict["ab"]: "AB",
        #     all_dimension_val_dict["sk"]: "SK",
        #     all_dimension_val_dict["mb"]: "MB",
        #     all_dimension_val_dict["bc"]: "BC",
        #     all_dimension_val_dict["qc"]: "QC",
        #     all_dimension_val_dict["nb"]: "NB",
        #     all_dimension_val_dict["ns"]: "NS",
        #     all_dimension_val_dict["nl"]: "NL",
        #     all_dimension_val_dict["pe"]: "PE",
        #     all_dimension_val_dict["nu"]: "NU",
        #     all_dimension_val_dict["nt"]: "NT",
        #     all_dimension_val_dict["yt"]: "YT",
        #     all_dimension_val_dict["atlantic"]: "ATLANTIC",
        #     all_dimension_val_dict["prairies"]: "PRAIRIE",
        #     all_dimension_val_dict["territories"]: "TERRITORIES",
        #     all_dimension_val_dict["men"]: "MEN",
        #     all_dimension_val_dict["women"]: "WOMEN",
        #     all_dimension_val_dict["boys"]: "BOYS",
        #     all_dimension_val_dict["girls"]: "GIRLS",
        #     all_dimension_val_dict["m"]: "MALES",
        #     all_dimension_val_dict["f"]: "FEMALES",
        #     all_dimension_val_dict["canada"]: "CANADA",
        #     # all_dimension_val_dict["male_alone"]: "MALE LIVING ALONE",
        #     # all_dimension_val_dict["female_alone"]: "FEMALE LIVING ALONE",
        #     # all_dimension_val_dict["couple_no_children"]: "COUPLE NO CHILDREN",
        #     # all_dimension_val_dict[
        #     #     "couple_with_childrenU18"
        #     # ]: "COUPLE WITH CHILD(REN) LESS THAN 18 YEARS OLD",
        #     # all_dimension_val_dict[
        #     #     "female_with_childrenU18"
        #     # ]: "FEMALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
        #     # all_dimension_val_dict[
        #     #     "male_with_childrenU18"
        #     # ]: "MALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
        #     # all_dimension_val_dict[
        #     #     "other_living_arrangements"
        #     # ]: "OTHER LIVING ARRANGEMENTS",
        # },
    }

    return export_mapping


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


# def deduce_dimension_type(record, csv_line_number):
#     dimension_deduced_bool = False
#     dimension_deduced = None
#     dimension_col_name = None

#     checking_column = "Geography"
#     geography = record[checking_column]
#     if geography and geography.lower() not in [
#         "canada",
#         "null",
#         "nan",
#         "",
#     ]:
#         # print("DIMESNION: ", geography, " FOR: ", record, "\n")
#         dimension_deduced_bool = True
#         dimension_deduced = geography
#         dimension_col_name = checking_column

#     checking_column = "Sex"
#     sex = record[checking_column]
#     if sex and sex.lower() not in ["both sexes", "null", "nan", ""]:
#         # print("DIMESNION: ", sex, " FOR: ", record, "\n")
#         if dimension_deduced_bool:
#             print(
#                 "WARNING ON LINE (",
#                 csv_line_number,
#                 "): DIMENSION ALREADY DEDUCED ",
#                 dimension_deduced,
#                 "\nNEW DIMENSION FOUND: ",
#                 sex,
#                 "\nPLEASE CHECK RECORD: ",
#                 record,
#             )
#             return None
#         else:
#             dimension_deduced_bool = True
#             dimension_deduced = sex
#             dimension_col_name = checking_column

#     checking_column = "Gender"
#     gender = record[checking_column]
#     if gender and gender.lower() not in [
#         "both genders",
#         "null",
#         "nan",
#         "",
#     ]:
#         # print("DIMESNION: ", gender, " FOR: ", record, "\n")
#         if dimension_deduced_bool:
#             print(
#                 "WARNING ON LINE (",
#                 csv_line_number,
#                 "): DIMENSION ALREADY DEDUCED ",
#                 dimension_deduced,
#                 "\nNEW DIMENSION FOUND: ",
#                 gender,
#                 "\nPLEASE CHECK RECORD: ",
#                 record,
#             )
#             return None
#         else:
#             dimension_deduced_bool = True
#             dimension_deduced = gender
#             dimension_col_name = checking_column

#     checking_column = "Age_Group"
#     age_group = record[checking_column]
#     if age_group and age_group.lower() not in ["null", "nan", ""]:
#         # print("DIMESNION: ", age_group, " FOR: ", record, "\n")
#         if dimension_deduced_bool:
#             print(
#                 "WARNING ON LINE (",
#                 csv_line_number,
#                 "): DIMENSION ALREADY DEDUCED ",
#                 dimension_deduced,
#                 "\nNEW DIMENSION FOUND: ",
#                 age_group,
#                 "\nPLEASE CHECK RECORD: ",
#                 record,
#             )
#             return None
#         else:
#             dimension_deduced_bool = True
#             dimension_deduced = age_group
#             dimension_col_name = checking_column

#     checking_column = "Geography"
#     if not dimension_deduced_bool and geography.lower() == "canada":
#         # print("DIMESNION: ", geography, " FOR: ", record, "\n")
#         if dimension_deduced_bool:
#             print(
#                 "WARNING ON LINE (",
#                 csv_line_number,
#                 "): DIMENSION ALREADY DEDUCED ",
#                 dimension_deduced,
#                 "\nNEW DIMENSION FOUND: ",
#                 geography,
#                 "\nPLEASE CHECK RECORD: ",
#                 record,
#             )
#             return None
#         else:
#             dimension_deduced_bool = True
#             dimension_deduced = geography
#             dimension_col_name = checking_column

#     if not dimension_deduced_bool:
#         print(
#             "WARNING ON LINE (",
#             csv_line_number,
#             "): DIMENSION NOT FOUND ",
#             "\nPLEASE CHECK RECORD: ",
#             record,
#         )
#         return None
#     return {
#         "dimension_col_name": dimension_col_name,
#         "dimension_value": dimension_deduced,
#     }
