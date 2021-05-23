import json
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pymongo.database import Collection
from starlette.responses import Response

from app.encrypt import hash_password
from app.schemas import LoginRequest

users = Mock(spec=Collection)


@pytest.fixture
def mock_users(mocker):
    mock = mocker.patch('app.db.get_user_collection')
    mock.return_value = users
    return mock.return_value


@pytest.fixture
def client(mock_users):
    from app.main import app
    return TestClient(app)


@pytest.fixture
def valid_request():
    return LoginRequest(email='atimin@gmail.com', password='pwd').json()


def test__login_ok(client, valid_request):
    users.find_one.return_value = {
        'email': 'atimin@gmail.com',
        'hashed_password': hash_password('pwd')
    }

    resp: Response = client.put('/auth/login', valid_request)

    users.find_one.assert_called_with({'email': 'atimin@gmail.com'})
    assert resp.status_code == 200
    assert 'access_token' in json.loads(resp.content)


def test__login_bad_email(client, valid_request):
    users.find_one.return_value = {
        'email': 'atimin@gmail.com',
        'hashed_password': hash_password('bad_pwd')
    }

    resp: Response = client.put('/auth/login', valid_request)
    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == 'Bad email or password'


def test__login_bad_password(client, valid_request):
    users.find_one.return_value = None

    resp: Response = client.put('/auth/login', valid_request)
    assert resp.status_code == 401
    assert json.loads(resp.content)['detail'] == 'Bad email or password'


def test__login_invalid_request(client):
    users.find_one.return_value = None

    resp: Response = client.put('/auth/login', json.dumps({'something': 'invalid'}))
    assert resp.status_code == 422
