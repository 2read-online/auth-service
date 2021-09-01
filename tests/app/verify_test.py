# pylint: disable=redefined-outer-name
"""Test verify processing"""
import time

import pytest
from cryptography.fernet import Fernet

from app.config import CONFIG
from app.db import User
from app.schemas import VerifyRequest
from tests.app.conftest import users, get_subject, get_detail


@pytest.fixture
def valid_request():
    """Valid request"""
    fernet = Fernet(CONFIG.fernet_key)
    return VerifyRequest(verification_hash=fernet.encrypt(b'atimin@gmail.com')).json()


def test__verify_and_login_ok(client, user_id, valid_request):
    """Should pass valid request and return access token"""
    users.find_one.return_value = {
        '_id': user_id,
        'email': 'atimin@gmail.com'
    }

    resp = client.post('/auth/verify', valid_request)

    users.find_one.assert_called_with({'email': 'atimin@gmail.com'})
    users.insert_one.assert_not_called()
    assert resp.status_code == 200
    assert get_subject(resp.content, 'access_token') == str(user_id)
    assert get_subject(resp.content, 'refresh_token') == str(user_id)


def test__verify_create_and_login_ok(client, user_id, valid_request):
    """Should create user if it doesnt exist"""
    users.find_one.return_value = None
    users.insert_one.return_value = user_id

    resp = client.post('/auth/verify', valid_request)

    users.find_one.assert_called_with({'email': 'atimin@gmail.com'})
    users.insert_one.assert_called_with(User(email='atimin@gmail.com').db())
    assert resp.status_code == 200
    assert get_subject(resp.content, 'access_token') == str(user_id)
    assert get_subject(resp.content, 'refresh_token') == str(user_id)


def test__wrong_verification_hash(client):
    """Should return 400 if hash is wrong"""
    resp = client.post('/auth/verify', VerifyRequest(verification_hash='XXXXXXX').json())
    assert resp.status_code == 400
    assert get_detail(resp.content) == 'Bad or expired verification link'


def test__expired_verification_hash(client):
    """Should return 400 if hash has expired"""
    expired_hash = Fernet(CONFIG.fernet_key) \
        .encrypt_at_time(b'atimin@gmail.com', int(time.time())
                         - (CONFIG.email_verification_ttl + 1))

    resp = client.post('/auth/verify', VerifyRequest(verification_hash=expired_hash).json())
    assert resp.status_code == 400
    assert get_detail(resp.content) == 'Bad or expired verification link'
