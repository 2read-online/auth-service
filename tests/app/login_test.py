# pylint: disable=redefined-outer-name
"""Test login processing"""
import json

import pytest
from bson import ObjectId

from app.encrypt import hash_password
from app.schemas import LoginRequest
from tests.app.conftest import users, get_subject


@pytest.fixture
def valid_request():
    """Valid request"""
    return LoginRequest(email='atimin@gmail.com', password='pwd').json()


def test__login_ok(client, user_id, valid_request):
    """Should pass valid request and return access token"""
    users.find_one.return_value = {
        '_id': user_id,
        'email': 'atimin@gmail.com',
        'hashed_password': hash_password('pwd')
    }

    resp = client.put('/auth/login', valid_request)

    users.find_one.assert_called_with({'email': 'atimin@gmail.com'})
    assert resp.status_code == 200
    assert get_subject(resp.content, 'access_token') == str(user_id)
    assert get_subject(resp.content, 'refresh_token') == str(user_id)


def test__login_bad_password(client, valid_request):
    """Should return 401 if password mismatches"""
    users.find_one.return_value = {
        '_id': ObjectId(),
        'email': 'atimin@gmail.com',
        'hashed_password': hash_password('bad_pwd')
    }

    resp = client.put('/auth/login', valid_request)
    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == 'Bad email or password'


def test__login_no_user(client, valid_request):
    """Should return 401 if the user is not found"""
    users.find_one.return_value = None

    resp = client.put('/auth/login', valid_request)
    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == 'Bad email or password'


def test__login_invalid_request(client):
    """Should return 422 and details if request is not valid"""
    users.find_one.return_value = None

    resp = client.put('/auth/login', json.dumps({'something': 'invalid'}))
    assert resp.status_code == 422
    assert json.loads(resp.content)['detail'] == [
        {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"},
        {"loc": ["body", "password"], "msg": "field required", "type": "value_error.missing"}]
