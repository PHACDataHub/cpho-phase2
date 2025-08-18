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
        for dimension_type in DimensionType.objects.exclude(
            is_literal=True
        ).all()
    }


@cache_within_request
def get_all_dimension_values() -> dict[str, DimensionValue]:
    return list(
        DimensionValue.objects.order_by("order")
        .prefetch_related("dimension_type")
        .all()
    )


@cache_within_request
def get_dimension_type_mapper_dict():
    all_dimension_dict = get_all_dimension_types_dict()

    return {d.get_excel_code(): d for d in all_dimension_dict.values()}


@cache_within_request
def get_non_literal_dimension_mapper_dict():
    """
    resulting dict helps map excel row values to dimension value lookups
    indexed by excel-code pairs for dim-type and dim-values
    e.g. { ("Province", "ON") : <DimensionValue for ontario...> , ... }
    """
    all_dimension_vals = get_all_dimension_values()

    def key_for_row(dim_val: DimensionValue):
        return (
            dim_val.dimension_type.get_excel_code(),
            dim_val.get_excel_code(),
        )

    r = {key_for_row(dim_val): dim_val for dim_val in all_dimension_vals}
    return r


def get_non_literal_dimension_mapper_dict_by_dimension_type():
    """
    nests the tuple key dict above
    turns { (dimension_code, dimension_code): mapped_value, ... }
    into { dimension_code: { dimension_code: mapped_value, ... }, ... }
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
        return val.get_excel_code()

    @classmethod
    def map_dimension_value(cls, val):
        return val.get_excel_code()

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
