from django.db.utils import IntegrityError

import pytest

from cpho.model_factories import (
    BenchmarkingFactory,
    IndicatorFactory,
    TrendAnalysisFactory,
)
from cpho.models import (
    Benchmarking,
    Country,
    DimensionType,
    DimensionValue,
    IndicatorDatum,
    Period,
)


def test_indicator_datum_predefined_dimension_uniqueness():
    p = Period.objects.first()
    p2 = Period.objects.last()
    ind = IndicatorFactory()

    sex_dim = DimensionType.objects.get(code="sex")
    male = sex_dim.possible_values.get(value="m")
    female = sex_dim.possible_values.get(value="f")

    ind.data.create(
        period=p,
        dimension_type=sex_dim,
        dimension_value=male,
        value=1,
    )
    # can use diff dimension values,
    ind.data.create(
        period=p,
        dimension_type=sex_dim,
        dimension_value=female,
        value=1,
    )
    # can use diff period,
    ind.data.create(
        period=p2,
        dimension_type=sex_dim,
        dimension_value=female,
        value=1,
    )

    with pytest.raises(IntegrityError):
        ind.data.create(
            period=p,
            dimension_type=sex_dim,
            dimension_value=male,
            literal_dimension_val="foo",
        )


def test_benchmarking_uniqueness():
    ind = IndicatorFactory()
    australia = Country.objects.get(name_en="Australia")

    BenchmarkingFactory(
        indicator=ind,
        oecd_country=australia,
        labels=Benchmarking.LABEL_CHOICES[0][0],
    )
    BenchmarkingFactory(
        indicator=ind,
        oecd_country=australia,
        labels=Benchmarking.LABEL_CHOICES[1][0],
    )

    with pytest.raises(IntegrityError):
        BenchmarkingFactory(
            indicator=ind,
            oecd_country=australia,
            labels=Benchmarking.LABEL_CHOICES[0][0],
        )


def test_trend_uniqueness():
    ind = IndicatorFactory()

    TrendAnalysisFactory(
        indicator=ind,
        year=2020,
    )
    TrendAnalysisFactory(
        indicator=ind,
        year=2021,
    )

    with pytest.raises(IntegrityError):
        TrendAnalysisFactory(
            indicator=ind,
            year=2021,
        )


def test_indicator_datum_literal_dimension_uniqueness():
    p = Period.objects.first()
    ind = IndicatorFactory()
    age_dim = DimensionType.objects.get(code="age")

    # can still create multiple records that have NULL dimension-values,
    ind.data.create(
        period=p,
        dimension_type=age_dim,
        dimension_value=None,
        literal_dimension_val="foo",
    )
    ind.data.create(
        period=p,
        dimension_type=age_dim,
        dimension_value=None,
        literal_dimension_val="bar",
    )
    # but can't use the exact same literal value,
    with pytest.raises(IntegrityError):
        ind.data.create(
            period=p,
            dimension_type=age_dim,
            dimension_value=None,
            literal_dimension_val="bar",
        )


def test_indicator_datum_version_annotations():
    p = Period.objects.first()
    ind = IndicatorFactory()
    m_dim_val = DimensionValue.objects.get(value="m")

    live_record = ind.data.create(
        period=p,
        value=1,
        dimension_type=m_dim_val.dimension_type,
        dimension_value=m_dim_val,
    )
    v1 = live_record.versions.get()

    live_record.reset_version_attrs()
    live_record.value = 2
    live_record.save()

    v2 = live_record.versions.last()
    v2.is_program_submitted = True
    v2.save()

    live_record.reset_version_attrs()
    live_record.value = 3
    live_record.save()

    v3 = live_record.versions.last()
    v3.is_hso_submitted = True
    v3.is_program_submitted = True
    v3.save()

    live_record.reset_version_attrs()
    live_record.value = 4
    live_record.save()

    v4 = live_record.versions.last()

    refetched_record = (
        IndicatorDatum.active_objects.all()
        .with_last_version_id()
        .with_last_submitted_version_id()
        .get(id=live_record.id)
    )
    assert refetched_record.last_version_id == v4.id
    assert refetched_record.last_submitted_version_id == v3.id
