from django.db.utils import IntegrityError

import pytest

from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, Period


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
