import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestApiDocumentationEndpoints:
    def test_schema_endpoint(self, api_client):
        url = reverse('schema')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'openapi' in response.content.decode('utf-8')

    def test_swagger_ui_endpoint(self, api_client):
        url = reverse('swagger-ui')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'swagger-ui' in response.content.decode('utf-8').lower()

    def test_redoc_endpoint(self, api_client):
        url = reverse('redoc')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'redoc' in response.content.decode('utf-8').lower()
