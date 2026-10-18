import pytest
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def ensure_site(db):
    """Ensure standard default Site exists for allauth and URL reversal."""
    Site.objects.get_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'Project Finder'})


@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient."""
    return APIClient()


@pytest.fixture
def user_credentials():
    """Default test user credentials."""
    return {
        'username': 'auth_tester',
        'email': 'auth_tester@example.com',
        'password': 'StrongPassword123!',
    }


@pytest.fixture
def test_user(db, user_credentials):
    """Create and return a standard test user."""
    user = User.objects.create_user(
        username=user_credentials['username'],
        email=user_credentials['email'],
        password=user_credentials['password'],
    )
    return user


@pytest.fixture
def auth_token(db, test_user):
    """Generate DRF token for test_user."""
    token, _ = Token.objects.get_or_create(user=test_user)
    return token


@pytest.fixture
def authenticated_client(api_client, auth_token):
    """DRF APIClient authenticated with test_user via Token."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
    return api_client
