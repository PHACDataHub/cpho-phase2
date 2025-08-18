from collections import defaultdict

from data_fetcher import cache_within_request

from cpho.models import DimensionType, DimensionValue, Period


def inverted_dict(d: dict):
    return {v: k for k, v in d.items()}


# these mapper dictionaries are keyed by CSV/excel format (often CAPS)
# values are DB representation (often snake_case)
# for export purposes, we often invert them

category_mapper = {
    "": "",
    "FACTORS INFLUENCING HEALTH": "factors_influencing_health",
    "GENERAL HEALTH STATUS": "general_health_status",
    "HEALTH OUTCOMES": "health_outcomes",
}

topic_mapper = {
    "": "",
    "SOCIAL FACTORS": "social_factors",
    "HEALTH STATUS": "health_status",
    "COMMUNICABLE DISEASES": "communicable_diseases",
    "SUBSTANCE USE": "substance_use",
    "CHILDHOOD AND FAMILY FACTORS": "childhood_and_family_factors",
    "CHRONIC DISEASES AND MENTAL HEALTH": "chronic_diseases_and_mental_health",
}

data_quality_mapper = {
    "": "",
    "CAUTION": "caution",
    "GOOD": "good",
    "ACCEPTABLE": "acceptable",
    "SUPPRESSED": "suppressed",
    "VERY GOOD": "very_good",
    "EXCELLENT": "excellent",
}

arrow_flag_mapper = {
    "": "",
    "UP": "up",
    "DOWN": "down",
}


reason_for_null_mapper = {
    "": "",
    "Suppressed": "suppressed",
    "Not available": "not_available",
}

value_unit_mapper = {
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
    "LITRES": "litres",
    "OTHER": "other",
}

value_displayed_mapper = {
    "": "",
    "%": "%",
    "DDDs PER 1,000 CENSUS INHABITANTS": "per_1k_census",
    "PER 10,000 PATIENT DAYS": "per_10k_patient_days",
    "PER 100,000 LIVE BIRTHS": "per_100k_live_births",
    "PER 100,000 POPULATION": "per_100k_population",
    "PER 100,000 POPULATION PER YEAR": "per_100k_population_per_year",
    "YEARS": "years",
    "LITRES": "litres",
    "OTHER": "other",
}


@cache_within_request
def get_all_periods_dict() -> dict[str, Period]:
    return {period.code: period for period in Period.objects.all()}


@cache_within_request
def get_all_dimension_types_dict() -> dict[str, DimensionType]:
    return {
        dimension_type.code: dimension_type
        for dimension_type in DimensionType.objects.all()
    }


@cache_within_request
def get_all_dimension_values_dict() -> dict[str, DimensionValue]:
    return {
        dimension_value.value: dimension_value
        for dimension_value in DimensionValue.objects.all()
    }


@cache_within_request
def get_dimension_type_mapper_dict():
    all_dimension_dict = get_all_dimension_types_dict()
    return {
        "Province": all_dimension_dict["province"],
        "Age Group": all_dimension_dict["age"],
        "Sex": all_dimension_dict["sex"],
        "Canada": all_dimension_dict["canada"],
        "Region": all_dimension_dict["region"],
        "Gender": all_dimension_dict["gender"],
        "Living Arrangement": all_dimension_dict["living_arrangement"],
        "Education Household": all_dimension_dict["education_household"],
        "Income Quintiles": all_dimension_dict["income_quintiles"],
    }


@cache_within_request
def get_non_literal_dimension_mapper_dict():
    all_dimension_val_dict = get_all_dimension_values_dict()

    return {
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
        ("Province", "CANADA"): all_dimension_val_dict["canada"],
        ("Region", "ATLANTIC"): all_dimension_val_dict["atlantic"],
        ("Region", "PRAIRIE"): all_dimension_val_dict["prairies"],
        ("Region", "TERRITORIES"): all_dimension_val_dict["territories"],
        ("Gender", "MEN"): all_dimension_val_dict["men"],
        ("Gender", "WOMEN"): all_dimension_val_dict["women"],
        ("Gender", "BOYS"): all_dimension_val_dict["boys"],
        ("Gender", "GIRLS"): all_dimension_val_dict["girls"],
        ("Gender", "MEN+"): all_dimension_val_dict["men_plus"],
        ("Gender", "WOMEN+"): all_dimension_val_dict["women_plus"],
        ("Gender", "ALL"): all_dimension_val_dict["all_genders"],
        ("Sex", "MALES"): all_dimension_val_dict["m"],
        ("Sex", "FEMALES"): all_dimension_val_dict["f"],
        ("Sex", "BOTH"): all_dimension_val_dict["both"],
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
    }


def get_non_literal_dimension_mapper_dict_by_dimension_type():
    """
    nests the tuple key dict above
    turns { (dimension_type, dimension_value): mapped_value, ... }
    into { dimension_type: { dimension_value: mapped_value, ... }, ... }
    """
    source = get_non_literal_dimension_mapper_dict()

    dest = defaultdict(dict)
    for (dim_type, dim_value), mapped_value in source.items():
        dest[dim_type][dim_value] = mapped_value
    return dest


class ImportMapper:

    @staticmethod
    def map_category(val):
        return category_mapper[val]

    @staticmethod
    def map_topic(val):
        return topic_mapper[val]

    @staticmethod
    def map_period(val):
        return get_all_periods_dict()[val]

    @staticmethod
    def map_dimension_type(val):
        d = get_dimension_type_mapper_dict()
        return d[val]

    @staticmethod
    def map_dimension_value(val):
        d = get_non_literal_dimension_mapper_dict()
        return d[val]

    @staticmethod
    def map_data_quality(val):
        return data_quality_mapper[val]

    @staticmethod
    def map_arrow_flag(val):
        return arrow_flag_mapper[val]

    @staticmethod
    def map_reason_for_null(val):
        return reason_for_null_mapper[val]

    @staticmethod
    def map_value_unit(val):
        return value_unit_mapper[val]

    @staticmethod
    def map_value_displayed(val):
        return value_displayed_mapper[val]


class ExportMapper:
    @staticmethod
    def map_category(val):
        return inverted_dict(category_mapper).get(val, "")

    @staticmethod
    def map_topic(val):
        return inverted_dict(topic_mapper).get(val, "")

    @staticmethod
    def map_period(val):
        mapper_dict = get_all_periods_dict()
        return inverted_dict(mapper_dict).get(val, "")

    @staticmethod
    def map_dimension_type(val):
        mapper_dict = get_dimension_type_mapper_dict()
        return inverted_dict(mapper_dict).get(val, "")

    @staticmethod
    @cache_within_request
    def get_dimension_value_mapper_dict():
        mapper_dict = get_non_literal_dimension_mapper_dict()
        # these are pairs of (dimension_type, dimension_value)
        # we just want the dimension value
        just_values = {k[1]: v for k, v in mapper_dict.items()}

        canada_val = DimensionValue.objects.get(
            dimension_type__code="province", value="canada"
        )
        just_values[canada_val] = "CANADA"

        return inverted_dict(just_values)

    @classmethod
    def map_dimension_value(cls, val):
        mapper_dict = cls.get_dimension_value_mapper_dict()
        return mapper_dict.get(val, "")

    @staticmethod
    def map_data_quality(val):
        return inverted_dict(data_quality_mapper).get(val, "")

    @staticmethod
    def map_arrow_flag(val):
        return inverted_dict(arrow_flag_mapper).get(val, "")

    @staticmethod
    def map_reason_for_null(val):
        return inverted_dict(reason_for_null_mapper).get(val, "")

    @staticmethod
    def map_value_unit(val):
        return inverted_dict(value_unit_mapper).get(val, "")

    @staticmethod
    def map_value_displayed(val):
        return inverted_dict(value_displayed_mapper).get(val, "")
