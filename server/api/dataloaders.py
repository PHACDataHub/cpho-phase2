from collections import defaultdict

from django.db.models import Q

from cpho.models import (
    Benchmarking,
    BenchmarkingHistory,
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    IndicatorDatumHistory,
    Period,
    TrendAnalysis,
    TrendAnalysisHistory,
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
            pk__in=version_ids,
            is_deleted=False,
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


class SubmittedDatumByIndicatorLoader(SingletonDataLoader):
    def batch_load(self, indicator_ids):
        data = IndicatorDatum.objects.filter(
            indicator_id__in=indicator_ids
        ).with_last_submitted_version_id()

        version_ids = [x.last_submitted_version_id for x in data]
        versions = IndicatorDatumHistory.objects.filter(
            pk__in=version_ids,
            is_deleted=False,
        ).select_related("period")

        versions_by_indicator = defaultdict(list)
        for version in versions:
            versions_by_indicator[version.indicator_id].append(version)

        return [
            versions_by_indicator[indicator_id]
            for indicator_id in indicator_ids
        ]


class SubmittedBenchmarkingByIndicatorLoader(SingletonDataLoader):
    def batch_load(self, indicator_ids):
        benchmarkings = Benchmarking.objects.filter(
            indicator_id__in=indicator_ids
        ).with_last_submitted_version_id()

        version_ids = [x.last_submitted_version_id for x in benchmarkings]
        versions = BenchmarkingHistory.objects.filter(
            pk__in=version_ids,
            is_deleted=False,
        ).select_related("oecd_country")

        versions_by_indicator = defaultdict(list)
        for version in versions:
            versions_by_indicator[version.indicator_id].append(version)

        return [
            versions_by_indicator[indicator_id]
            for indicator_id in indicator_ids
        ]


class SubmittedTrendAnalysisByIndicatorLoader(SingletonDataLoader):
    def batch_load(self, indicator_ids):
        trend_analyses = TrendAnalysis.objects.filter(
            indicator_id__in=indicator_ids
        ).with_last_submitted_version_id()

        version_ids = [x.last_submitted_version_id for x in trend_analyses]
        versions = TrendAnalysisHistory.objects.filter(
            pk__in=version_ids,
            is_deleted=False,
        )

        versions_by_indicator = defaultdict(list)
        for version in versions:
            versions_by_indicator[version.indicator_id].append(version)

        return [
            versions_by_indicator[indicator_id]
            for indicator_id in indicator_ids
        ]


class SubmittedPeriodsByIndicatorLoader(SingletonDataLoader):
    def batch_load(self, indicator_ids):
        data = IndicatorDatum.objects.filter(
            indicator_id__in=indicator_ids
        ).with_last_submitted_version_id()

        version_ids = [x.last_submitted_version_id for x in data]
        versions = IndicatorDatumHistory.objects.filter(
            pk__in=version_ids,
            is_deleted=False,
        ).select_related("period")

        periods_by_indicator = defaultdict(set)
        for version in versions:
            periods_by_indicator[version.indicator_id].add(version.period)

        return [
            periods_by_indicator[indicator_id]
            for indicator_id in indicator_ids
        ]
