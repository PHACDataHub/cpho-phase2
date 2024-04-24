from cpho.constants import SUBMISSION_STATUSES
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
from cpho.queries import get_submission_statuses
from cpho.services import SubmitIndicatorDataService

# These tests are very heavy on data-generation

NO_DATA_TRIPLE = ["no_data"] * 3


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
            if status == "no_data":
                continue

            datum = ind.data.create(
                period=period,
                dimension_type=dim_type,
                dimension_value=dim_val,
                value=1.0,
            )
            if status in ["both_modified", "hso_modified", "program_modified"]:
                # submit a version and then create a new one
                v1 = datum.versions.last()
                if status in ["both_modified", "hso_modified"]:
                    v1.is_hso_submitted = True
                if status in ["both_modified", "program_modified"]:
                    v1.is_program_submitted = True
                v1.save()

                datum.reset_version_attrs()
                datum.save()

            elif status in [
                "both_submitted",
                "hso_submitted",
                "program_submitted",
            ]:
                v1 = datum.versions.last()
                if status in ["both_submitted", "hso_submitted"]:
                    v1.is_hso_submitted = True
                if status in ["both_submitted", "program_submitted"]:
                    v1.is_program_submitted = True
                v1.save()

            elif status == "not_yet_submitted":
                pass

            else:
                raise Exception("Unknown status...")

    return ind, period, dim1, dim2, dim3


def test_hso_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["hso_submitted"] * 3,
        xyz=["hso_submitted"] * 3,
        ijk=["hso_submitted"] * 3,
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
    }


def test_program_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["program_submitted"] * 3,
        xyz=["program_submitted"] * 3,
        ijk=["program_submitted"] * 3,
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }


def test_both_submitted():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["both_submitted"] * 3,
        xyz=["both_submitted"] * 3,
        ijk=["both_submitted"] * 3,
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
    }


def test_both_submitted_with_edit():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["both_submitted"] * 3,
        xyz=["both_submitted"] * 3,
        ijk=[
            "both_submitted",
            "both_modified",
            "both_submitted",
        ],
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "hso_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "program_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
    }


def test_hso_submitted_with_edit():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["hso_submitted"] * 3,
        xyz=["hso_submitted"] * 3,
        ijk=[
            "hso_submitted",
            "hso_modified",
            "hso_submitted",
        ],
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "hso_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        },
        "program_global_status": SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
    }


def test_program_submitted_with_edit():
    ind, period, abc_dim, xyz_dim, ijk_dim = create_data(
        abc=["program_submitted"] * 3,
        xyz=["program_submitted"] * 3,
        ijk=[
            "program_submitted",
            "program_modified",
            "program_submitted",
        ],
    )
    statuses = get_submission_statuses(ind, period)
    assert statuses == {
        "hso_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        },
        "hso_global_status": SUBMISSION_STATUSES.NOT_YET_SUBMITTED,
        "program_statuses_by_dimension_type_id": {
            abc_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            xyz_dim.id: SUBMISSION_STATUSES.PROGRAM_SUBMITTED,
            ijk_dim.id: SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
        },
        "program_global_status": SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION,
    }
