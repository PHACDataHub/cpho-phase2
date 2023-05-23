from cpho.model_factories import IndicatorDatumFactory
from cpho.models import Indicator, IndicatorDatum


def test_indicators_are_versioned():
    datum = IndicatorDatumFactory(value=1.0)
    assert datum.versions.count() == 1
    assert datum.versions.first().value == 1.0

    datum.reset_version_attrs()
    datum.value = 2.0
    datum.save()

    assert datum.versions.count() == 2
    assert datum.versions.first().value == 1.0
    assert datum.versions.last().value == 2.0
