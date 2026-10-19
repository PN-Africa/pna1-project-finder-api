import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_database_connection():
    User = get_user_model()
    assert User.objects.count() >= 0


def test_health_check_endpoint(api_client):
    response = api_client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy', 'service': 'project-finder'}

    response_healthz = api_client.get('/healthz/')
    assert response_healthz.status_code == 200
    assert response_healthz.json() == {'status': 'healthy', 'service': 'project-finder'}
