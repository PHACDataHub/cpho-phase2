from django.urls import reverse

from cpho.constants import SUBMISSION_STATUSES
from cpho.model_factories import (
    BenchmarkingFactory,
    IndicatorFactory,
    TrendAnalysisFactory,
)
from cpho.models import (
    Benchmarking,
    Country,
    Indicator,
    IndicatorMetaDataSubmission,
    TrendAnalysis,
)
from cpho.services import SubmitIndicatorMetaDataService

from .utils_for_tests import patch_rules


def test_submit_metadata(vanilla_user, vanilla_user_client):
    ind = IndicatorFactory()
    canada = Country.objects.get(name_en="Canada")
    australia = Country.objects.get(name_en="Australia")
    b1 = BenchmarkingFactory(indicator=ind, oecd_country=canada, value=21.0)
    b2 = BenchmarkingFactory(indicator=ind, oecd_country=australia, value=31.0)
    t1 = TrendAnalysisFactory(indicator=ind, year=2016, data_point=21.0)
    t2 = TrendAnalysisFactory(indicator=ind, year=2017, data_point=31.0)

    ind = Indicator.objects.get(pk=ind.pk)
    b1 = Benchmarking.objects.get(pk=b1.pk)
    b2 = Benchmarking.objects.get(pk=b2.pk)
    t1 = TrendAnalysis.objects.get(pk=t1.pk)
    t2 = TrendAnalysis.objects.get(pk=t2.pk)

    b1.value = 22.0
    b1.save()
    b2.value = 32.0
    b2.save()
    t1.data_point = 22.0
    t1.save()
    t2.data_point = 32.0
    t2.save()

    version_ids = SubmitIndicatorMetaDataService(
        ind, "program", vanilla_user
    )._get_version_ids_to_submit()

    assert len(version_ids["benchmarking"]) == 2
    assert len(version_ids["trend"]) == 2

    assert version_ids["indicator"] == ind.versions.last().pk
    assert set(version_ids["benchmarking"]) == {
        b1.versions.last().pk,
        b2.versions.last().pk,
    }
    assert set(version_ids["trend"]) == {
        t1.versions.last().pk,
        t2.versions.last().pk,
    }

    url = reverse("submit_metadata", args=[ind.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 302
    with patch_rules(can_submit_indicator=False):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 403

    assert IndicatorMetaDataSubmission.objects.count() == 1

    assert t1.versions.last().is_program_submitted
    assert t2.versions.last().is_program_submitted
    assert b1.versions.last().is_program_submitted
    assert b2.versions.last().is_program_submitted
    assert ind.versions.last().is_program_submitted

    url = reverse("submit_metadata", args=[ind.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.post(url, {"submission_type": "hso"})
        assert resp.status_code == 302
    with patch_rules(can_submit_indicator=False):
        resp = vanilla_user_client.post(url, {"submission_type": "hso"})
        assert resp.status_code == 403

    assert IndicatorMetaDataSubmission.objects.count() == 2

    assert t1.versions.last().is_program_submitted
    assert t2.versions.last().is_program_submitted
    assert b1.versions.last().is_program_submitted
    assert b2.versions.last().is_program_submitted
    assert ind.versions.last().is_program_submitted

    assert t1.versions.last().is_hso_submitted
    assert t2.versions.last().is_hso_submitted
    assert b1.versions.last().is_hso_submitted
    assert b2.versions.last().is_hso_submitted
    assert ind.versions.last().is_hso_submitted


def test_metadata_review_page(vanilla_user, vanilla_user_client):
    ind = IndicatorFactory()
    canada = Country.objects.get(name_en="Canada")
    australia = Country.objects.get(name_en="Australia")
    b1 = BenchmarkingFactory(indicator=ind, oecd_country=canada, value=21.0)
    b2 = BenchmarkingFactory(indicator=ind, oecd_country=australia, value=31.0)
    t1 = TrendAnalysisFactory(indicator=ind, year=2016, data_point=21.0)
    t2 = TrendAnalysisFactory(indicator=ind, year=2017, data_point=31.0)

    ind = Indicator.objects.get(pk=ind.pk)
    b1 = Benchmarking.objects.get(pk=b1.pk)
    b2 = Benchmarking.objects.get(pk=b2.pk)
    t1 = TrendAnalysis.objects.get(pk=t1.pk)
    t2 = TrendAnalysis.objects.get(pk=t2.pk)

    b1.value = 22.0
    b1.save()
    b2.value = 32.0
    b2.save()
    t1.data_point = 22.0
    t1.save()
    t2.data_point = 32.0
    t2.save()

    url = reverse("review_metadata", args=[ind.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
        assert (
            resp.context["submission_statuses"]["indicator_status"]
            == SUBMISSION_STATUSES.NOT_YET_SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["benchmarking_status"]
            == SUBMISSION_STATUSES.NOT_YET_SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["trend_status"]
            == SUBMISSION_STATUSES.NOT_YET_SUBMITTED
        )

    SubmitIndicatorMetaDataService(ind, "program", vanilla_user).perform()

    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
        assert (
            resp.context["submission_statuses"]["indicator_status"]
            == SUBMISSION_STATUSES.PROGRAM_SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["benchmarking_status"]
            == SUBMISSION_STATUSES.PROGRAM_SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["trend_status"]
            == SUBMISSION_STATUSES.PROGRAM_SUBMITTED
        )

    SubmitIndicatorMetaDataService(ind, "hso", vanilla_user).perform()

    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
        assert (
            resp.context["submission_statuses"]["indicator_status"]
            == SUBMISSION_STATUSES.SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["benchmarking_status"]
            == SUBMISSION_STATUSES.SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["trend_status"]
            == SUBMISSION_STATUSES.SUBMITTED
        )

    b1 = Benchmarking.objects.get(pk=b1.pk)
    b1.value = 66.0
    b1.save()
    t2 = TrendAnalysis.objects.get(pk=t2.pk)
    t2.data_point = 66.0
    t2.save()

    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200
        print(resp.context["submission_statuses"])
        assert (
            resp.context["submission_statuses"]["indicator_status"]
            == SUBMISSION_STATUSES.SUBMITTED
        )
        assert (
            resp.context["submission_statuses"]["benchmarking_status"]
            == SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
        )
        assert (
            resp.context["submission_statuses"]["trend_status"]
            == SUBMISSION_STATUSES.MODIFIED_SINCE_LAST_SUBMISSION
        )
