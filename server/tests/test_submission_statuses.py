from cpho.constants import APPROVAL_STATUSES
from cpho.model_factories import (
    DimensionTypeFactory,
    DimensionValueFactory,
    IndicatorFactory,
)
from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDataSubmission,
    Period,
)
from cpho.queries import get_approval_statuses
from cpho.services import SubmitIndicatorDataService

# These tests are very heavy on data-generation

NO_DATA_TRIPLE = [APPROVAL_STATUSES.NO_DATA] * 3


def create_data(abc, xyz=NO_DATA_TRIPLE, ijk=NO_DATA_TRIPLE):
    period = Period.objects.first()
    ind = IndicatorFactory()

    dim1 = DimensionTypeFactory(code="abc")
    dim1_val_a = DimensionValueFactory(dimension_type=dim1, value="a")
    dim1_val_b = DimensionValueFactory(dimension_type=dim1, value="b")
    dim1_val_c = DimensionValueFactory(dimension_type=dim1, value="c")

    dim2 = DimensionTypeFactory(code="xyz")
    dim2_val_x = DimensionValueFactory(dimension_type=dim2, value="x")
    dim2_val_y = DimensionValueFactory(dimension_type=dim2, value="y")
    dim2_val_z = DimensionValueFactory(dimension_type=dim2, value="z")

    dim3 = DimensionTypeFactory(code="ijk")
    dim3_val_i = DimensionValueFactory(dimension_type=dim3, value="i")
    dim3_val_j = DimensionValueFactory(dimension_type=dim3, value="j")
    dim3_val_k = DimensionValueFactory(dimension_type=dim3, value="k")

    vals_by_dim = {
        dim1: zip([dim1_val_a, dim1_val_b, dim1_val_c], abc),
        dim2: zip([dim2_val_x, dim2_val_y, dim2_val_z], xyz),
        dim3: zip([dim3_val_i, dim3_val_j, dim3_val_k], ijk),
    }

    for dim_type, val_statuses in vals_by_dim.items():
        for dim_val, status in val_statuses:
            if status == APPROVAL_STATUSES.NO_DATA:
                continue

            datum = ind.data.create(
                period=period,
                dimension_type=dim_type,
                dimension_value=dim_val,
                value=1.0,
            )
            if status == APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION:
                # submit a version and then create a new one
                v1 = datum.versions.last()
                v1.is_hso_approved = True
                v1.is_program_approved = True
                v1.save()

                datum.reset_version_attrs()
                datum.save()

            elif status == APPROVAL_STATUSES.SUBMITTED:
                v1 = datum.versions.last()
                v1.is_hso_approved = True
                v1.is_program_approved = True
                v1.save()

            elif status == APPROVAL_STATUSES.PROGRAM_SUBMITTED:
                v1 = datum.versions.last()
                v1.is_program_approved = True
                v1.save()

            elif status == APPROVAL_STATUSES.NOT_YET_SUBMITTED:
                pass

            else:
                raise Exception("Unknown status...")

    return ind, period, dim1, dim2, dim3


def test_fully_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=[APPROVAL_STATUSES.SUBMITTED] * 3,
        xyz=[APPROVAL_STATUSES.SUBMITTED] * 3,
        ijk=[APPROVAL_STATUSES.SUBMITTED] * 3,
    )
    statuses = get_approval_statuses(ind, period)
    assert statuses == {
        "statuses_by_dimension_type_id": {
            abc_dim.id: APPROVAL_STATUSES.SUBMITTED,
            xyz_dim.id: APPROVAL_STATUSES.SUBMITTED,
            ijk_dim.id: APPROVAL_STATUSES.SUBMITTED,
        },
        "global_status": APPROVAL_STATUSES.SUBMITTED,
    }


def test_fully_submitted_with_program_caveat():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=[APPROVAL_STATUSES.SUBMITTED] * 3,
        xyz=[APPROVAL_STATUSES.SUBMITTED] * 3,
        ijk=[
            APPROVAL_STATUSES.SUBMITTED,
            APPROVAL_STATUSES.PROGRAM_SUBMITTED,
            APPROVAL_STATUSES.SUBMITTED,
        ],
    )
    statuses = get_approval_statuses(ind, period)
    assert statuses == {
        "statuses_by_dimension_type_id": {
            abc_dim.id: APPROVAL_STATUSES.SUBMITTED,
            xyz_dim.id: APPROVAL_STATUSES.SUBMITTED,
            ijk_dim.id: APPROVAL_STATUSES.PROGRAM_SUBMITTED,
        },
        "global_status": APPROVAL_STATUSES.PROGRAM_SUBMITTED,
    }


def test_fully_submitted_with_edit():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=[APPROVAL_STATUSES.SUBMITTED] * 3,
        xyz=[APPROVAL_STATUSES.SUBMITTED] * 3,
        ijk=[
            APPROVAL_STATUSES.SUBMITTED,
            APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
            APPROVAL_STATUSES.SUBMITTED,
        ],
    )
    statuses = get_approval_statuses(ind, period)
    assert statuses == {
        "statuses_by_dimension_type_id": {
            abc_dim.id: APPROVAL_STATUSES.SUBMITTED,
            xyz_dim.id: APPROVAL_STATUSES.SUBMITTED,
            ijk_dim.id: APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "global_status": APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
    }


def test_modified_takes_precedence_over_program_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=[APPROVAL_STATUSES.SUBMITTED] * 3,
        xyz=[APPROVAL_STATUSES.SUBMITTED] * 3,
        ijk=[
            APPROVAL_STATUSES.PROGRAM_SUBMITTED,
            APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
            APPROVAL_STATUSES.SUBMITTED,
        ],
    )
    statuses = get_approval_statuses(ind, period)
    assert statuses == {
        "statuses_by_dimension_type_id": {
            abc_dim.id: APPROVAL_STATUSES.SUBMITTED,
            xyz_dim.id: APPROVAL_STATUSES.SUBMITTED,
            ijk_dim.id: APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "global_status": APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
    }


def test_not_submitted_takes_precedence_over_modified_since_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=[APPROVAL_STATUSES.SUBMITTED] * 3,
        xyz=[APPROVAL_STATUSES.SUBMITTED] * 3,
        ijk=[
            APPROVAL_STATUSES.NOT_YET_SUBMITTED,
            APPROVAL_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
            APPROVAL_STATUSES.SUBMITTED,
        ],
    )
    statuses = get_approval_statuses(ind, period)
    assert statuses == {
        "statuses_by_dimension_type_id": {
            abc_dim.id: APPROVAL_STATUSES.SUBMITTED,
            xyz_dim.id: APPROVAL_STATUSES.SUBMITTED,
            ijk_dim.id: APPROVAL_STATUSES.NOT_YET_SUBMITTED,
        },
        "global_status": APPROVAL_STATUSES.NOT_YET_SUBMITTED,
    }
