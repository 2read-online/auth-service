# pylint: disable=redefined-outer-name
"""Test register processing"""
import json

import pytest

from app.encrypt import hash_with_salt
from app.schemas import RegisterRequest
from tests.app.conftest import users


@pytest.fixture
def valid_request():
    """Valid request"""
    return RegisterRequest(email='test@test.com', password='password12',
                           password_confirmation='password12').json()


def test__register_ok(client, valid_request):
    """Should register a user with valid data"""
    users.find_one.return_value = None

    resp = client.post('/auth/register', valid_request)

    users.find_one.assert_called_with({'email': 'test@test.com'})
    users.insert_one.assert_called_with({'email': 'test@test.com',
                                         'hashed_password': hash_with_salt('password12')})
    assert resp.status_code == 200


def test__user_exists(client, valid_request):
    """Should return 409 if user already exists"""
    users.find_one.return_value = {}
    resp = client.post('/auth/register', valid_request)

    assert resp.status_code == 409
    assert json.loads(resp.content)['detail'] == 'User already exists'
