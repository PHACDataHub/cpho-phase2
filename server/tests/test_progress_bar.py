from django.urls import reverse

from bs4 import BeautifulSoup

from cpho.constants import SUBMISSION_STATUSES
from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDataSubmission,
    Period,
)
from cpho.services import SubmitIndicatorDataService

from .utils_for_tests import patch_rules


def progress_bar_percent(ind, period, vanilla_user_client, precent_list):
    url = reverse("view_indicator_for_period", args=[ind.id, period.id])
    with patch_rules(can_view_indicator_data=True):
        resp = vanilla_user_client.get(url)
    assert resp.status_code == 200
    html_content = resp.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    # find class="progress-bar" and check that it has the correct attributes
    progress_bar = soup.find(class_="progress-data-entered")
    assert progress_bar is not None
    assert progress_bar.has_attr("aria-valuenow")
    assert progress_bar["aria-valuenow"] == str(precent_list[0])

    progress_bar = soup.find(class_="progress-program-approved")
    assert progress_bar is not None
    assert progress_bar.has_attr("aria-valuenow")
    assert progress_bar["aria-valuenow"] == str(precent_list[1])

    progress_bar = soup.find(class_="progress-hso-approved")
    assert progress_bar is not None
    assert progress_bar.has_attr("aria-valuenow")
    assert progress_bar["aria-valuenow"] == str(precent_list[2])


def test_progress_bar(vanilla_user, vanilla_user_client):
    period = Period.objects.first()
    ind = IndicatorFactory()
    sex_dim = DimensionType.objects.get(code="sex")
    for dimension_type in ind.relevant_dimensions.all():
        if dimension_type != sex_dim:
            for dimension_value in dimension_type.possible_values.all():
                datum = IndicatorDatumFactory(
                    indicator=ind,
                    period=period,
                    dimension_type=dimension_type,
                    dimension_value=dimension_value,
                )
                datum.save()

    progress_bar_percent(ind, period, vanilla_user_client, [100, 0, 0])

    url = reverse("submit_indicator_data_all", args=[ind.id, period.id])
    with patch_rules(can_submit_as_hso_or_program=True):
        resp = vanilla_user_client.post(url, {"submission_type": "program"})
        assert resp.status_code == 302

    progress_bar_percent(ind, period, vanilla_user_client, [100, 100, 0])

    with patch_rules(can_submit_as_hso_or_program=True):
        resp = vanilla_user_client.post(url, {"submission_type": "hso"})
        assert resp.status_code == 302

    progress_bar_percent(ind, period, vanilla_user_client, [100, 100, 100])

    for dimension_value in sex_dim.possible_values.all():
        datum = IndicatorDatumFactory(
            indicator=ind,
            period=period,
            dimension_type=sex_dim,
            dimension_value=dimension_value,
        )
        datum.save()
    progress_bar_percent(ind, period, vanilla_user_client, [100, 0, 0])
