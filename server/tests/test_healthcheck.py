from django.test.client import Client
from django.urls import reverse


def test_healthcheck():
    url = reverse("simple_healthcheck")

    response = Client().get(url, follow=False)

    assert response.status_code == 200
