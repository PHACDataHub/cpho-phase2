from django.urls import reverse

from bs4 import BeautifulSoup
from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorFactory
from cpho.models import Indicator


def test_create_indicator(vanilla_user_client):
    url = reverse("create_indicator")
    with patch_rules(can_create_indicator=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200

        response = vanilla_user_client.post(
            url,
            data={
                "name": "Test Indicator",
                "name_fr": "Test Indicator FR",
                "category": Indicator.CATEGORY_CHOICES[-1][0],
                "topic": Indicator.TOPIC_CHOICES[-1][0],
                "detailed_indicator": "Test Detailed Indicator",
                "sub_indicator_measurement": "Test Sub Indicator Measurement",
                "sub_indicator_measurement_fr": "Test Sub Indicator Measurement FR",
                "measure_text_fr": "Test Measure Text FR",
                "impact_text_fr": "Test Impact Text FR",
                "title_age_fr": "Test Title Age FR",
                "title_province_territory_fr": "Test Title Province Territory FR",
            },
        )
        assert response.status_code == 302

    indicator = Indicator.objects.latest("pk")
    assert indicator.name == "Test Indicator"
    assert indicator.name_fr == "Test Indicator FR"
    assert (
        indicator.sub_indicator_measurement_fr
        == "Test Sub Indicator Measurement FR"
    )
    assert indicator.measure_text_fr == "Test Measure Text FR"
    assert indicator.impact_text_fr == "Test Impact Text FR"
    assert indicator.title_age_fr == "Test Title Age FR"
    assert (
        indicator.title_province_territory_fr
        == "Test Title Province Territory FR"
    )


def test_edit_indicator(vanilla_user_client):
    ind = IndicatorFactory()
    url = reverse("edit_indicator", args=[ind.id])

    with patch_rules(can_access_indicator=True, can_edit_indicator=False):
        response = vanilla_user_client.get(url)
        assert response.status_code == 403

    with patch_rules(can_edit_indicator=True):
        resp = vanilla_user_client.get(url)
        assert resp.status_code == 200

    data = {
        "name": "Test Indicator",
        "category": ind.category,
        "topic": ind.topic,
        "detailed_indicator": "Test Detailed Indicator",
        "sub_indicator_measurement": "Test Sub Indicator Measurement",
    }
    with patch_rules(can_edit_indicator=True):
        resp = vanilla_user_client.post(url, data=data)
        assert resp.status_code == 302
        assert resp.url == reverse("view_indicator", args=[ind.id])


def test_hso_fields_hidden_and_disabled(vanilla_user_client):
    """
    There are three "tiers",
    1. fields editable by both admin and program users (in this test: measure_text)
    2. fields visible to programs but editable by admin only (in this test: name)
    3. fields only visible (and editable) by admin (in this test: title_overall)

    """
    ind = IndicatorFactory(
        measure_text="initial measure text",
        name="initial name",
        title_overall="initial title overall",
    )
    url = reverse("edit_indicator", args=[ind.id])

    with patch_rules(can_edit_indicator=True, is_admin_or_hso=False):
        resp = vanilla_user_client.get(url)

        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")

        measure_text_input = soup.select_one("input[name='measure_text']")
        assert "disabled" not in measure_text_input.attrs

        name_input = soup.select_one("input[name='name']")
        assert "disabled" in name_input.attrs

        title_overall_input = soup.select("input[name='title_overall']")
        assert not title_overall_input

    assert resp.status_code == 200
    ctx = resp.context
    form_obj = ctx["form"]
    assert form_obj.fields["title_overall"].disabled

    with patch_rules(can_edit_indicator=True, is_admin_or_hso=False):
        resp = vanilla_user_client.post(
            url,
            data={
                "title_overall": "new title overall",
                "name": "new name",
                "measure_text": "new measure text",
            },
        )

    assert resp.status_code == 302

    ind.refresh_from_db()

    assert ind.title_overall == "initial title overall"
    assert ind.name == "initial name"
    assert ind.measure_text == "new measure text"


def test_hso_fields_enabled(vanilla_user_client):
    """
    still same three "tiers",
    1. fields editable by both admin and program users (in this test: measure_text)
    2. fields visible to programs but editable by admin only (in this test: name)
    3. fields only visible (and editable) by admin (in this test: title_overall)

    """
    ind = IndicatorFactory(
        measure_text="initial measure text",
        title_overall="initial title overall",
        name="initial name",
    )
    url = reverse("edit_indicator", args=[ind.id])

    with patch_rules(can_edit_indicator=True, is_admin_or_hso=True):
        resp = vanilla_user_client.get(url)

    soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
    name_input = soup.select_one("input[name='name']")
    assert "disabled" not in name_input.attrs

    title_overall_input = soup.select_one("input[name='title_overall']")
    assert "disabled" not in title_overall_input

    measure_text_input = soup.select_one("input[name='measure_text']")
    assert "disabled" not in measure_text_input.attrs

    assert resp.status_code == 200
    ctx = resp.context
    form_obj = ctx["form"]
    assert not form_obj.fields["title_overall"].disabled

    with patch_rules(can_edit_indicator=True, is_admin_or_hso=True):
        resp = vanilla_user_client.post(
            url,
            data={
                "title_overall": "new title overall",
                "name": "new name",
                "measure_text": "new measure text",
            },
        )
    assert resp.status_code == 302

    ind.refresh_from_db()

    assert ind.title_overall == "new title overall"
    assert ind.name == "new name"
    assert ind.measure_text == "new measure text"
