import pytest
from rest_framework.test import APIClient
from wallet.models import User

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username='test_user', email='test@gmail.com', password='password')
    return user
