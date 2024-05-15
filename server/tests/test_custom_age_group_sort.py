import copy
import random

from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import DimensionType, Indicator, IndicatorDatum, Period
from cpho.views import age_group_sort


def test_custom_age_group_sort():
    ind = IndicatorFactory()
    ind.save()
    age_dimension = DimensionType.objects.get(code="age")
    period = Period.objects.first()

    literal_values_range = [
        " < 5",
        "10 -15",
        "16",
        "20 -25",
        " 29 ",
        "30 to  35",
        "40 -  45 ",
        " 47",
        "50 - 55 ",
        "60to 65",
        "70-75 ",
        "80 -85",
        "87 ",
        " 90to95",
        " 100 +",
        "hello",
        "World",
    ]
    shuffle = copy.deepcopy(literal_values_range)
    assert shuffle == literal_values_range
    random.shuffle(shuffle)
    assert shuffle != literal_values_range
    for i, literal_value in enumerate(shuffle):
        obj = IndicatorDatumFactory(
            indicator=ind,
            period=period,
            dimension_type=age_dimension,
            value=i,
            literal_dimension_val=literal_value,
        )
        obj.save()

    data = IndicatorDatum.objects.filter(indicator=ind)
    sorted_list = age_group_sort(data)
    sorted_list_vals = [d.literal_dimension_val for d in sorted_list]
    assert sorted_list_vals == literal_values_range
