from api.dataloaders import (
    PeriodByIdLoader,
    SubmittedDatumByIndicatorYearLoader,
)
from promise import Promise
from tests.api.api_test_utils import get_promise_result
from tests.utils_for_tests import submit_indicator_datum

from cpho.model_factories import IndicatorFactory
from cpho.models import DimensionType, DimensionValue, Period


def test_promise_behaviour(django_assert_max_num_queries):
    dataloader_instance_cache = {}

    y2021 = Period.objects.get(
        year=2021, year_type=Period.CALENDAR_YEAR_TYPE, quarter=None
    )
    fy2021 = Period.objects.get(
        year=2021, year_type=Period.FISCAL_YEAR_TYPE, quarter=None
    )

    with django_assert_max_num_queries(1):

        def promise_code():
            p1 = PeriodByIdLoader(dataloader_instance_cache).load(y2021.id)
            p2 = PeriodByIdLoader(dataloader_instance_cache).load(fy2021.id)
            p1, p2 = yield Promise.all([p1, p2]).get()
            return p1, p2

        calendar_year, fy_year = get_promise_result(promise_code)
    assert calendar_year == y2021
    assert fy_year == fy2021


def test_basic_loader(django_assert_max_num_queries):
    dataloader_instance_cache = {}

    y2021 = Period.objects.get(
        year=2021, year_type=Period.CALENDAR_YEAR_TYPE, quarter=None
    )
    fy2021 = Period.objects.get(
        year=2021, year_type=Period.FISCAL_YEAR_TYPE, quarter=None
    )

    with django_assert_max_num_queries(1):

        def promise_code():
            PeriodByIdLoader(dataloader_instance_cache).load_many(
                [y2021.id, fy2021.id]
            )
            calendar_year = yield PeriodByIdLoader(
                dataloader_instance_cache
            ).load(y2021.id)
            fy_year = yield PeriodByIdLoader(dataloader_instance_cache).load(
                fy2021.id
            )
            return calendar_year, fy_year

        calendar_year, fy_year = get_promise_result(promise_code)
    assert calendar_year == y2021
    assert fy_year == fy2021


def test_submitted_datum_by_indicator_year_loader(
    django_assert_max_num_queries,
):
    ind1 = IndicatorFactory()
    ind2 = IndicatorFactory()

    y2021_q1 = Period.objects.get(
        year=2021, year_type=Period.FISCAL_YEAR_TYPE, quarter=1
    )
    y2021_q2 = Period.objects.get(
        year=2021, year_type=Period.FISCAL_YEAR_TYPE, quarter=2
    )
    y2022 = Period.objects.get(
        year=2022, year_type=Period.FISCAL_YEAR_TYPE, quarter=None
    )

    dim_type = DimensionType.objects.first()
    dim_val = dim_type.possible_values.first()

    ind1_datum_q1 = ind1.data.create(
        period=y2021_q1,
        value=1,
        dimension_value=dim_val,
        dimension_type=dim_type,
    )
    v1_not_submitted = ind1_datum_q1.versions.last()
    v1_not_submitted.program_submitted = True
    v1_not_submitted = True
    ind1_datum_q1.reset_version_attrs()

    ind1_datum_q1.value = 2
    ind1_datum_q1.save()
    submit_indicator_datum(ind1_datum_q1)
    v2_submitted = ind1_datum_q1.versions.last()
    ind1_datum_q1.reset_version_attrs()
    ind1_datum_q1.value = 3
    ind1_datum_q1.save()

    ind1_datum_q2 = ind1.data.create(
        period=y2021_q2,
        value=1,
        dimension_value=dim_val,
        dimension_type=dim_type,
    )
    q2_v1 = ind1_datum_q2.versions.last()
    submit_indicator_datum(ind1_datum_q2)

    # this one isn't submitted at all
    ind1_datum_y2022 = ind1.data.create(
        period=y2022, value=1, dimension_value=dim_val, dimension_type=dim_type
    )

    # finally, ind2 also get a submitted datum for 2022
    ind2_datum_y2022 = ind2.data.create(
        period=y2022, value=1, dimension_value=dim_val, dimension_type=dim_type
    )
    submit_indicator_datum(ind2_datum_y2022)
    ind2_2022_submitted = ind2_datum_y2022.versions.last()

    dataloader_instance_cache = {}

    def promise_code():
        data = yield SubmittedDatumByIndicatorYearLoader(
            dataloader_instance_cache
        ).load_many(
            [
                (ind1.id, 2021),
                (ind2.id, 2021),
                (ind1.id, 2022),
                (ind2.id, 2022),
            ]
        )
        return data

    with django_assert_max_num_queries(2):
        # this dataloader makes 2 queries per batch
        (
            i1_2021_data,
            i2_2021_data,
            i1_2022_data,
            i2_2022_data,
        ) = get_promise_result(promise_code)

    assert i1_2021_data == [v2_submitted, q2_v1]
    assert i2_2021_data == []
    assert i1_2022_data == []
    assert i2_2022_data == [ind2_2022_submitted]
