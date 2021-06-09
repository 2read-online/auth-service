# pylint: disable=redefined-outer-name
"""Test login processing"""
import json

import pytest
from bson import ObjectId
from fastapi_jwt_auth import AuthJWT

from app.encrypt import hash_password
from app.schemas import LoginRequest
from tests.app.conftest import users


@pytest.fixture
def valid_request():
    """Valid request"""
    return LoginRequest(email='atimin@gmail.com', password='pwd').json()


def test__login_ok(client, valid_request):
    """Should pass valid request and return access token"""
    users.find_one.return_value = {
        '_id': ObjectId('60c0b2d700569d97f8a93dcd'),
        'email': 'atimin@gmail.com',
        'hashed_password': hash_password('pwd')
    }

    resp = client.put('/auth/login', valid_request)

    users.find_one.assert_called_with({'email': 'atimin@gmail.com'})
    assert resp.status_code == 200

    data = json.loads(resp.content)
    auth = AuthJWT()
    jwt = auth.get_raw_jwt(data['access_token'])
    assert jwt['sub'] == '60c0b2d700569d97f8a93dcd'


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
