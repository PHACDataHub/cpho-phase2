from collections import defaultdict

from django.db.models import Q

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    IndicatorDatumHistory,
    Period,
)

from .util import (
    AbstractChildModelByAttrLoader,
    PrimaryKeyDataLoaderFactory,
    SingletonDataLoader,
)

PeriodByIdLoader = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(Period)
IndicatorByIdLoader = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(
    Indicator
)
DimensionTypeByIdLoader = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(
    DimensionType
)
DimensionValueByIdLoader = PrimaryKeyDataLoaderFactory.get_model_by_id_loader(
    DimensionValue
)


class SubmittedDatumByIndicatorYearLoader(SingletonDataLoader):
    """
    uses (indicator_id, year) as keys, returns a list of data per key
    """

    def batch_load(self, indicator_id_year_int_pairs):
        filter_condition = Q()
        for indicator_id, year in indicator_id_year_int_pairs:
            filter_condition |= Q(indicator_id=indicator_id, period__year=year)

        data = IndicatorDatum.objects.filter(
            filter_condition
        ).with_last_submitted_version_id()

        version_ids = [x.last_submitted_version_id for x in data]
        versions = IndicatorDatumHistory.objects.filter(
            pk__in=version_ids
        ).select_related("period")

        versions_by_pair = defaultdict(list)
        for version in versions:
            versions_by_pair[
                (version.indicator_id, version.period.year)
            ].append(version)

        return [
            versions_by_pair[(indicator_id, year)]
            for indicator_id, year in indicator_id_year_int_pairs
        ]
