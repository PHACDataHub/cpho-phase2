from cpho.models import DimensionType, DimensionValue


def upload_mapper():
    all_dimensions = DimensionType.objects.all()
    all_dimension_vals = DimensionValue.objects.all()

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
            "Province": all_dimensions.get(code="province"),
            "Age Group": all_dimensions.get(code="age"),
            "Sex": all_dimensions.get(code="sex"),
            "Canada": all_dimensions.get(code="canada"),
            "Region": all_dimensions.get(code="region"),
            "Gender": all_dimensions.get(code="gender"),
        },
        "non_literal_dimension_value_mapper": {
            ("Province", "ON"): all_dimension_vals.get(
                dimension_type__code="province", value="on"
            ),
            ("Province", "AB"): all_dimension_vals.get(
                dimension_type__code="province", value="ab"
            ),
            ("Province", "SK"): all_dimension_vals.get(
                dimension_type__code="province", value="sk"
            ),
            ("Province", "MB"): all_dimension_vals.get(
                dimension_type__code="province", value="mb"
            ),
            ("Province", "BC"): all_dimension_vals.get(
                dimension_type__code="province", value="bc"
            ),
            ("Province", "QC"): all_dimension_vals.get(
                dimension_type__code="province", value="qc"
            ),
            ("Province", "NB"): all_dimension_vals.get(
                dimension_type__code="province", value="nb"
            ),
            ("Province", "NS"): all_dimension_vals.get(
                dimension_type__code="province", value="ns"
            ),
            ("Province", "NL"): all_dimension_vals.get(
                dimension_type__code="province", value="nl"
            ),
            ("Province", "PE"): all_dimension_vals.get(
                dimension_type__code="province", value="pe"
            ),
            ("Province", "NU"): all_dimension_vals.get(
                dimension_type__code="province", value="nu"
            ),
            ("Province", "NT"): all_dimension_vals.get(
                dimension_type__code="province", value="nt"
            ),
            ("Province", "YT"): all_dimension_vals.get(
                dimension_type__code="province", value="yt"
            ),
            ("Region", "ATLANTIC"): all_dimension_vals.get(
                dimension_type__code="region", value="atlantic"
            ),
            ("Region", "PRAIRIE"): all_dimension_vals.get(
                dimension_type__code="region", value="prairies"
            ),
            ("Region", "TERRITORIES"): all_dimension_vals.get(
                dimension_type__code="region", value="territories"
            ),
            ("Gender", "MEN"): all_dimension_vals.get(
                dimension_type__code="gender", value="men"
            ),
            ("Gender", "WOMEN"): all_dimension_vals.get(
                dimension_type__code="gender", value="women"
            ),
            ("Gender", "BOYS"): all_dimension_vals.get(
                dimension_type__code="gender", value="boys"
            ),
            ("Gender", "GIRLS"): all_dimension_vals.get(
                dimension_type__code="gender", value="girls"
            ),
            ("Sex", "MALES"): all_dimension_vals.get(
                dimension_type__code="sex", value="m"
            ),
            ("Sex", "FEMALES"): all_dimension_vals.get(
                dimension_type__code="sex", value="f"
            ),
            ("Canada", "CANADA"): all_dimension_vals.get(
                dimension_type__code="canada", value="canada"
            ),
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
