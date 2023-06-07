from django.utils.translation import get_language


def get_lang_code():
    lang_locale = get_language()
    if "-ca" not in lang_locale:
        raise Exception("Unexpected language locale: {}".format(lang_locale))
    return lang_locale.split("-ca")[0]


def dropdown_mapper():
    return {
        "indicator_category": {
            "": "--",
            "factors_influencing_health": "Factors Influencing Health",
            "general_health_status": "General Health Status",
            "health_outcomes": "Health Outcomes",
        },
        "indicator_sub_category": {
            "": "--",
            "childhood_and_family_risk_and_protective_factors": "Childhood and Family Risk and Protective Factors",
            "social_factors": "Social Factors",
            "substance_use": "Substance Use",
            "health_status": "Health Status",
            "chronic_diseases_and_mental_health": "Chronic Diseases and Mental Health",
            "communicable_diseases": "Communicable Diseases",
        },
        "indicator_data_data_quality": {
            "": "--",
            "caution": "Caution",
            "acceptable": "Acceptable",
            "good": "Good",
            "excellent": "Excellent",
        },
        "indicator_data_value_unit": {
            "": "--",
            "%": "%",
            "per_100k": "Per 100K",
            "other": "Other",
        },
    }
