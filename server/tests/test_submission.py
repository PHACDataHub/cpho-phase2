from django.urls import reverse

from cpho.constants import SUBMISSION_STATUSES
from cpho.model_factories import IndicatorFactory
from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDataSubmission,
    Period,
)
from cpho.services import SubmitIndicatorDataService


def test_submit_all_dimensions(vanilla_user, vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")
    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="m"),
        value=9.0,
    )
    female_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="f"),
        value=1.0,
    )
    female_record.reset_version_attrs()
    female_record.value = 2.0
    female_record.save()
    canada_record = ind.data.create(
        period=period,
        dimension_type=DimensionType.objects.get(code="canada"),
        dimension_value=DimensionType.objects.get(
            code="canada"
        ).possible_values.get(),
        value=5.0,
    )

    version_ids = SubmitIndicatorDataService(
        ind, period, None, "hso", vanilla_user
    )._get_version_ids_to_submit()

    assert len(version_ids) == 3
    assert set(version_ids) == {
        female_record.versions.last().pk,
        male_record.versions.last().pk,
        canada_record.versions.last().pk,
    }
    url = reverse("submit_indicator_data_all", args=[ind.id, period.id])
    resp = vanilla_user_client.post(url, {"submission_type": "program"})
    assert resp.status_code == 302

    assert IndicatorDataSubmission.objects.count() == 1
    assert female_record.versions.last().is_program_submitted
    assert not female_record.versions.first().is_program_submitted
    assert male_record.versions.last().is_program_submitted
    assert canada_record.versions.last().is_program_submitted
    assert not canada_record.versions.last().is_hso_submitted

    resp = vanilla_user_client.post(url, {"submission_type": "hso"})
    assert resp.status_code == 302
    assert female_record.versions.last().is_hso_submitted
    assert female_record.versions.last().is_program_submitted


def test_review_page(vanilla_user, vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    sex_cat = DimensionType.objects.get(code="sex")
    male_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="m"),
        value=9.0,
    )
    female_record = ind.data.create(
        period=period,
        dimension_type=sex_cat,
        dimension_value=sex_cat.possible_values.get(value="f"),
        value=1.0,
    )
    female_record.reset_version_attrs()
    female_record.value = 2.0
    female_record.save()
    canada_record = ind.data.create(
        period=period,
        dimension_type=DimensionType.objects.get(code="canada"),
        dimension_value=DimensionType.objects.get(
            code="canada"
        ).possible_values.get(),
        value=5.0,
    )

    # test that the review page when no submissions exist,
    global_url = reverse("review_indicator_data_all", args=[ind.id, period.id])
    sex_url = reverse(
        "review_indicator_data", args=[ind.id, period.id, sex_cat.id]
    )

    assert vanilla_user_client.get(global_url).status_code == 200
    assert vanilla_user_client.get(sex_url).status_code == 200

    # test that the review page when submissions exist
    SubmitIndicatorDataService(
        ind, period, sex_cat, "program", vanilla_user
    ).perform()

    assert vanilla_user_client.get(global_url).status_code == 200
    assert vanilla_user_client.get(sex_url).status_code == 200

    SubmitIndicatorDataService(
        ind, period, sex_cat, "hso", vanilla_user
    ).perform()
    assert vanilla_user_client.get(global_url).status_code == 200
    assert vanilla_user_client.get(sex_url).status_code == 200

    # test that the review page when there is a new modification,
    female_record.reset_version_attrs()
    female_record.value = 3.0
    female_record.save()
    assert vanilla_user_client.get(global_url).status_code == 200
    assert vanilla_user_client.get(sex_url).status_code == 200
