import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework import status
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str

User = get_user_model()


@pytest.mark.django_db
class TestRegistrationEndpoint:
    """Tests for POST /api/auth/registration/ endpoint."""

    url = '/api/auth/registration/'

    def test_registration_success(self, api_client):
        payload = {
            'username': 'newuser123',
            'email': 'newuser123@example.com',
            'password1': 'SecurePass987!',
            'password2': 'SecurePass987!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        assert 'key' in response.data or 'access' in response.data
        assert User.objects.filter(username='newuser123').exists()

    def test_registration_password_mismatch(self, api_client):
        payload = {
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password1': 'SecurePass987!',
            'password2': 'DifferentPass123!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password2' in response.data or 'non_field_errors' in response.data
        assert not User.objects.filter(username='mismatch_user').exists()

    def test_registration_duplicate_username(self, api_client, test_user, user_credentials):
        payload = {
            'username': user_credentials['username'],
            'email': 'different_email@example.com',
            'password1': 'SecurePass987!',
            'password2': 'SecurePass987!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_registration_invalid_email(self, api_client):
        payload = {
            'username': 'invalid_email_user',
            'email': 'not-a-valid-email',
            'password1': 'SecurePass987!',
            'password2': 'SecurePass987!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestLoginEndpoint:
    """Tests for POST /api/auth/login/ endpoint."""

    url = '/api/auth/login/'

    def test_login_success(self, api_client, test_user, user_credentials):
        payload = {
            'username': user_credentials['username'],
            'password': user_credentials['password'],
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert 'key' in response.data or 'access' in response.data

    def test_login_invalid_password(self, api_client, test_user, user_credentials):
        payload = {
            'username': user_credentials['username'],
            'password': 'WrongPassword123!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data

    def test_login_nonexistent_user(self, api_client):
        payload = {
            'username': 'ghost_user',
            'password': 'SomePassword123!',
        }
        response = api_client.post(self.url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserDetailsEndpoint:
    """Tests for GET and PATCH /api/auth/user/ endpoint."""

    url = '/api/auth/user/'

    def test_get_user_profile_authenticated(self, authenticated_client, test_user):
        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == test_user.username
        assert response.data['email'] == test_user.email

    def test_get_user_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_user_profile(self, authenticated_client, test_user):
        payload = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
        }
        response = authenticated_client.patch(self.url, payload)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'UpdatedFirst'
        assert response.data['last_name'] == 'UpdatedLast'

        test_user.refresh_from_db()
        assert test_user.first_name == 'UpdatedFirst'
        assert test_user.last_name == 'UpdatedLast'


@pytest.mark.django_db
class TestLogoutEndpoint:
    """Tests for POST /api/auth/logout/ endpoint."""

    url = '/api/auth/logout/'

    def test_logout_authenticated(self, authenticated_client):
        response = authenticated_client.post(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('detail') in ['Successfully logged out.', 'Success']

    def test_token_invalidation_after_logout(self, authenticated_client, auth_token):
        # 1. Logout
        logout_response = authenticated_client.post(self.url)
        assert logout_response.status_code == status.HTTP_200_OK

        # 2. Verify token was deleted from database
        from rest_framework.authtoken.models import Token
        assert not Token.objects.filter(key=auth_token.key).exists()

        # 3. Subsequent request with previous token must fail
        profile_response = authenticated_client.get('/api/auth/user/')
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordResetEndpoints:
    """Tests for password reset request and confirm flows."""

    reset_request_url = '/api/auth/password/reset/'
    reset_confirm_url = '/api/auth/password/reset/confirm/'

    def test_password_reset_request_sends_email(self, api_client, test_user):
        response = api_client.post(
            self.reset_request_url,
            {'email': test_user.email},
            HTTP_HOST='localhost:8000',
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert test_user.email in mail.outbox[0].to
        # Check that the email contains the generated confirm URL
        assert '/password-reset/confirm/' in mail.outbox[0].body

    def test_password_reset_request_nonexistent_email(self, api_client):
        response = api_client.post(
            self.reset_request_url,
            {'email': 'unknown@example.com'},
            HTTP_HOST='localhost:8000',
        )

        assert response.status_code == status.HTTP_200_OK
        # Email anti-enumeration: no email is actually sent
        assert len(mail.outbox) == 0

    def test_password_reset_confirm_link_get_json(self, api_client, test_user):
        uid = user_pk_to_url_str(test_user)
        token = default_token_generator.make_token(test_user)
        confirm_url = reverse('password_reset_confirm', args=[uid, token])

        response = api_client.get(confirm_url, HTTP_ACCEPT='application/json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['uid'] == uid
        assert response.data['token'] == token

    def test_password_reset_confirm_link_get_html(self, api_client, test_user):
        uid = user_pk_to_url_str(test_user)
        token = default_token_generator.make_token(test_user)
        confirm_url = reverse('password_reset_confirm', args=[uid, token])

        response = api_client.get(confirm_url, HTTP_ACCEPT='text/html')

        assert response.status_code == status.HTTP_200_OK
        assert b'<form id="resetForm">' in response.content

    def test_password_reset_confirm_success(self, api_client, test_user):
        uid = user_pk_to_url_str(test_user)
        token = default_token_generator.make_token(test_user)
        new_password = 'BrandNewStrongPassword123!'

        payload = {
            'uid': uid,
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password,
        }
        response = api_client.post(self.reset_confirm_url, payload)

        assert response.status_code == status.HTTP_200_OK

        # Verify login succeeds with the new password
        login_res = api_client.post('/api/auth/login/', {
            'username': test_user.username,
            'password': new_password,
        })
        assert login_res.status_code == status.HTTP_200_OK

    def test_password_reset_confirm_invalid_token(self, api_client, test_user):
        uid = user_pk_to_url_str(test_user)
        payload = {
            'uid': uid,
            'token': 'invalid-token-12345',
            'new_password1': 'NewPass1234!',
            'new_password2': 'NewPass1234!',
        }
        response = api_client.post(self.reset_confirm_url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'token' in response.data


@pytest.mark.django_db
class TestPasswordChangeEndpoint:
    """Tests for POST /api/auth/password/change/ endpoint."""

    url = '/api/auth/password/change/'

    def test_password_change_success(self, authenticated_client, test_user, user_credentials, api_client):
        new_password = 'ChangedPassword999!'
        payload = {
            'old_password': user_credentials['password'],
            'new_password1': new_password,
            'new_password2': new_password,
        }
        response = authenticated_client.post(self.url, payload)

        assert response.status_code == status.HTTP_200_OK

        # Verify user can log in with new password
        login_res = api_client.post('/api/auth/login/', {
            'username': test_user.username,
            'password': new_password,
        })
        assert login_res.status_code == status.HTTP_200_OK

    def test_password_change_unauthenticated(self, api_client):
        response = api_client.post(self.url, {
            'new_password1': 'ChangedPass123!',
            'new_password2': 'ChangedPass123!',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
