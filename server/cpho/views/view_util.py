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
    return {
        "category_mapper": {
            "": "",
            "FACTORS INFLUENCING HEALTH": "factors_influencing_health",
            "GENERAL HEALTH STATUS": "general_health_status",
            "HEALTH OUTCOMES": "health_outcomes",
        },
        "subcategory_mapper": {
            "": "",
            "SOCIAL FACTORS": "social_factors",
            "HEALTH STATUS": "health_status",
            "COMMUNICABLE DISEASES": "communicable_diseases",
            "SUBSTANCE USE": "substance_use",
            "CHILDHOOD AND FAMILY FACTORS": "childhood_and_family_risk_and_protective_factors",
            "CHILDHOOD AND FAMILY RISK FACTORS": "childhood_and_family_risk_and_protective_factors",
            "CHRONIC DISEASES AND MENTAL HEALTH": "chronic_diseases_and_mental_health",
        },
        "data_quality_mapper": {
            "": "",
            "CAUTION": "caution",
            "GOOD": "good",
            "ACCEPTABLE": "acceptable",
            "SUPPRESSED": "suppressed",
            "VERY GOOD": "excellent",
        },
        "value_unit_mapper": {
            "": "",
            "%": "%",
            "PER 100,000": "per_100k",
            "YEARS": "years",
            "PER 1,000 CENSUS INHABITANTS": "per_100k_census",
            "PER 10,000 PATIENT DAYS": "per_100k_patient_days",
            "PER 100,000 LIVE BIRTHS": "per_100k_live_births",
        },
        "dimension_type_mapper": {
            "Province": all_dimension_dict["province"],
            "Age Group": all_dimension_dict["age"],
            "Sex": all_dimension_dict["sex"],
            "Canada": all_dimension_dict["canada"],
            "Region": all_dimension_dict["region"],
            "Gender": all_dimension_dict["gender"],
        },
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
