# pylint: disable=redefined-outer-name
"""Test login processing"""
import json

import pytest
from cryptography.fernet import Fernet

from app.config import CONFIG
from app.schemas import LoginRequest
from tests.app.conftest import users


@pytest.fixture
def valid_request():
    """Valid request"""
    return LoginRequest(email='atimin@gmail.com').json()


def test__login_ok(client, redis, valid_request):
    """Should pass valid request and return access token"""
    fernet = Fernet(CONFIG.fernet_key)
    resp = client.put('/auth/login', valid_request)

    assert redis.xadd.call_args.args[0] == '/auth/login'
    assert redis.xadd.call_args.args[1]['email'] == 'atimin@gmail.com'
    assert fernet.decrypt(redis.xadd.call_args.args[1]['verification_hash']) == b'atimin@gmail.com'
    assert resp.status_code == 200
    assert resp.content == b'{}'


def test__login_invalid_request(client):
    """Should return 422 and details if request is not valid"""
    users.find_one.return_value = None

    resp = client.put('/auth/login', json.dumps({'something': 'invalid'}))
    assert resp.status_code == 422
    assert json.loads(resp.content)['detail'] == [
        {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}]
