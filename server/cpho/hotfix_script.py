import datetime

from django.db import transaction

relevant_indicator_ids = [
    148,
    140,  # opoid
    138,  # opoid death
    129,  # community belonging
    149,  # perceived mental health
    122,  # low birth weight
    160,  # dementia
    162,  # diabetes
]

from cpho.views.indicators import IndicatorForm

FIELDS_TO_RESTORE = [
    *IndicatorForm.hso_only_field_names,
    *[f for f in IndicatorForm.base_fields.keys() if f.endswith("_fr")],
]

danielle_id = 204
restore_date = datetime.datetime(2025, 1, 19)


with transaction.atomic():
    for indicator in Indicator.objects.filter(id__in=relevant_indicator_ids):
        restore_version = (
            indicator.versions.filter(timestamp__lte=restore_date)
            .order_by("-pk")
            .first()
        )
        print("\n\n restore version:", restore_version.__dict__)
        print(restore_version.timestamp, restore_version.edited_by)
        for field_name in FIELDS_TO_RESTORE:
            # print( f"Setting {field_name} on {indicator} from {getattr(indicator,field_name)} to {getattr(restore_version, field_name)}" )
            setattr(
                indicator, field_name, getattr(restore_version, field_name)
            )
            indicator.save()
