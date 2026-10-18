import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_database_connection():
    User = get_user_model()
    assert User.objects.count() >= 0
