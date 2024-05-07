from django.urls import reverse

from bs4 import BeautifulSoup
from phac_aspc.rules import patch_rules

from cpho.model_factories import IndicatorDatumFactory, IndicatorFactory
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)


def test_relevant_dimensions(vanilla_user, vanilla_user_client):
    p = Period.objects.first()
    ind = IndicatorFactory()
    sex_dim = DimensionType.objects.get(code="sex")
    gender_dim = DimensionType.objects.get(code="gender")

    assert sex_dim in ind.relevant_dimensions.all()

    ind.relevant_dimensions.remove(sex_dim)
    ind.save()
    ind.refresh_from_db()

    ind = Indicator.objects.get(id=ind.id)
    assert sex_dim not in ind.relevant_dimensions.all()

    # removing sex from relevant dimensions
    # sex dimension should not be visible anywhere
    url_view_period = reverse("view_indicator_for_period", args=[ind.id, p.id])
    with patch_rules(can_access_indicator=True):
        resp = vanilla_user_client.get(url_view_period)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="h5")
        headers_str = str(headers)
        assert sex_dim.name_en not in headers_str
        assert gender_dim.name_en in headers_str

    url_manage_data = reverse("manage_indicator_data_all", args=[ind.id, p.id])
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        resp = vanilla_user_client.get(url_manage_data)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="card-header")
        headers_str = str(headers)
        assert sex_dim.name_en not in headers_str
        assert gender_dim.name_en in headers_str

    url_review_data = reverse("review_indicator_data_all", args=[ind.id, p.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url_review_data)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="h5")
        headers_str = str(headers)
        assert sex_dim.name_en not in headers_str
        assert gender_dim.name_en in headers_str

    # adding sex data for period
    possible_dimension_value = sex_dim.possible_values.all()
    datum_male = IndicatorDatumFactory(
        indicator=ind,
        dimension_value=possible_dimension_value[0],
        period=p,
        dimension_type=sex_dim,
    )
    datum_male.save()
    datum_female = IndicatorDatumFactory(
        indicator=ind,
        dimension_value=possible_dimension_value[1],
        period=p,
        dimension_type=sex_dim,
    )
    datum_female.save()

    # sex data should show up in all views
    # although it is not in relevant dimensions as it has data for period
    url_view_period = reverse("view_indicator_for_period", args=[ind.id, p.id])
    with patch_rules(can_access_indicator=True):
        resp = vanilla_user_client.get(url_view_period)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="h5")
        headers_str = str(headers)
        assert sex_dim.name_en in headers_str
        assert gender_dim.name_en in headers_str

    url_manage_data = reverse("manage_indicator_data_all", args=[ind.id, p.id])
    with patch_rules(
        can_edit_indicator_data=True, can_view_indicator_data=True
    ):
        resp = vanilla_user_client.get(url_manage_data)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="card-header")
        headers_str = str(headers)
        assert sex_dim.name_en in headers_str
        assert gender_dim.name_en in headers_str

    url_review_data = reverse("review_indicator_data_all", args=[ind.id, p.id])
    with patch_rules(can_submit_indicator=True):
        resp = vanilla_user_client.get(url_review_data)
        assert resp.status_code == 200
        html_content = resp.content.decode("utf-8")
        soup = BeautifulSoup(html_content, "html.parser")
        headers = soup.find_all(class_="h5")
        headers_str = str(headers)
        assert sex_dim.name_en in headers_str
        assert gender_dim.name_en in headers_str
