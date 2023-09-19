from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.views.generic import TemplateView, View

from cpho.models import DimensionType, DimensionValue, Period


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
            "CHILDHOOD AND FAMILY FACTORS": "childhood_and_family_risk_and_protective_factors",
            "CHILDHOOD AND FAMILY RISK FACTORS": "childhood_and_family_risk_and_protective_factors",
            "CHRONIC DISEASES AND MENTAL HEALTH": "chronic_diseases_and_mental_health",
        },
        "age_group_type_mapper": {
            "": "",
            "5 Year": "five_year",
            "Grade": "grade",
            "Life Course": "life_course",
            "Setting": "setting",
        },
        "data_quality_mapper": {
            "": "",
            "CAUTION": "caution",
            "GOOD": "good",
            "ACCEPTABLE": "acceptable",
            "SUPPRESSED": "suppressed",
            "VERY GOOD": "very good",
        },
        "pt_data_availability_mapper": {
            "": "",
            "Available": "available",
            "Suppressed": "suppressed",
            "Not available": "not_available",
        },
        "value_unit_mapper": {
            "": "",
            "AGE-STANDARDIZED RATE": "age_rate",
            "CRUDE RATE": "crude_rate",
            "DEFINED DAILY DOSE/1,000 CENSUS": "daily_dose_per_1k_census",
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
        "dimension_type_mapper": {
            "Province": all_dimension_dict["province"],
            "Age Group": all_dimension_dict["age"],
            "Sex": all_dimension_dict["sex"],
            "Canada": all_dimension_dict["canada"],
            "Region": all_dimension_dict["region"],
            "Gender": all_dimension_dict["gender"],
            "Living Arrangement": all_dimension_dict["living_arrangement"],
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
            ("Sex", "MALES"): all_dimension_val_dict["m"],
            ("Sex", "FEMALES"): all_dimension_val_dict["f"],
            ("Canada", "CANADA"): all_dimension_val_dict["canada"],
            (
                "Living Arrangement",
                "MALE LIVING ALONE",
            ): all_dimension_val_dict["male_alone"],
            (
                "Living Arrangement",
                "FEMALE LIVING ALONE",
            ): all_dimension_val_dict["female_alone"],
            (
                "Living Arrangement",
                "COUPLE NO CHILDREN",
            ): all_dimension_val_dict["couple_no_children"],
            (
                "Living Arrangement",
                "COUPLE WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            ): all_dimension_val_dict["couple_with_childrenU18"],
            (
                "Living Arrangement",
                "FEMALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            ): all_dimension_val_dict["female_with_childrenU18"],
            (
                "Living Arrangement",
                "MALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            ): all_dimension_val_dict["male_with_childrenU18"],
            (
                "Living Arrangement",
                "OTHER LIVING ARRANGEMENTS",
            ): all_dimension_val_dict["other_living_arrangements"],
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
        "age_group_type_mapper": {
            v: k for k, v in upload_mapping["age_group_type_mapper"].items()
        },
        "data_quality_mapper": {
            v: k for k, v in upload_mapping["data_quality_mapper"].items()
        },
        "pt_data_availability_mapper": {
            v: k
            for k, v in upload_mapping["pt_data_availability_mapper"].items()
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
            all_dimension_val_dict["on"]: "ON",
            all_dimension_val_dict["ab"]: "AB",
            all_dimension_val_dict["sk"]: "SK",
            all_dimension_val_dict["mb"]: "MB",
            all_dimension_val_dict["bc"]: "BC",
            all_dimension_val_dict["qc"]: "QC",
            all_dimension_val_dict["nb"]: "NB",
            all_dimension_val_dict["ns"]: "NS",
            all_dimension_val_dict["nl"]: "NL",
            all_dimension_val_dict["pe"]: "PE",
            all_dimension_val_dict["nu"]: "NU",
            all_dimension_val_dict["nt"]: "NT",
            all_dimension_val_dict["yt"]: "YT",
            all_dimension_val_dict["atlantic"]: "ATLANTIC",
            all_dimension_val_dict["prairies"]: "PRAIRIE",
            all_dimension_val_dict["territories"]: "TERRITORIES",
            all_dimension_val_dict["men"]: "MEN",
            all_dimension_val_dict["women"]: "WOMEN",
            all_dimension_val_dict["boys"]: "BOYS",
            all_dimension_val_dict["girls"]: "GIRLS",
            all_dimension_val_dict["m"]: "MALES",
            all_dimension_val_dict["f"]: "FEMALES",
            all_dimension_val_dict["canada"]: "CANADA",
            all_dimension_val_dict["male_alone"]: "MALE LIVING ALONE",
            all_dimension_val_dict["female_alone"]: "FEMALE LIVING ALONE",
            all_dimension_val_dict["couple_no_children"]: "COUPLE NO CHILDREN",
            all_dimension_val_dict[
                "couple_with_childrenU18"
            ]: "COUPLE WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            all_dimension_val_dict[
                "female_with_childrenU18"
            ]: "FEMALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            all_dimension_val_dict[
                "male_with_childrenU18"
            ]: "MALE LONE PARENT WITH CHILD(REN) LESS THAN 18 YEARS OLD",
            all_dimension_val_dict[
                "other_living_arrangements"
            ]: "OTHER LIVING ARRANGEMENTS",
        },
    }

    return export_mapping


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
