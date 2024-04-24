from django.urls import reverse

from phac_aspc.rules import patch_rules

from cpho.model_factories import BenchmarkingFactory, IndicatorFactory
from cpho.models import Country
from cpho.views import BenchmarkingForm, ReadOnlyBenchmarkingForm


def test_benchmarking_permissions(vanilla_user_client):
    ind = IndicatorFactory()
    ind.save()
    country = Country.objects.get(name_en="Canada")
    data = BenchmarkingFactory(indicator=ind, oecd_country=country, value=1)
    data.save()
    url = reverse("manage_benchmarking_data", args=[ind.id])

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=False):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
        formset = response.context["benchmarking_formset"]
        for form in formset:
            assert isinstance(form, ReadOnlyBenchmarkingForm)

    with patch_rules(can_view_benchmarking=True, can_edit_benchmarking=True):
        response = vanilla_user_client.get(url)
        assert response.status_code == 200
        formset = response.context["benchmarking_formset"]
        for form in formset:
            assert isinstance(form, BenchmarkingForm)
