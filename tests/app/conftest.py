# pylint: skip-file
import json
from typing import Dict
from unittest.mock import Mock

import pytest
from bson import ObjectId
from fastapi_jwt_auth import AuthJWT
from pymongo.collection import Collection
from starlette.testclient import TestClient

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
def user_id() -> ObjectId:
    return ObjectId('60c0b2d700569d97f8a93dcd')


@pytest.fixture
def refresh_token(user_id) -> str:
    auth = AuthJWT()
    return auth.create_refresh_token(subject=str(user_id))


@pytest.fixture
def headers(refresh_token: str) -> Dict[str, str]:
    return {'Authorization': f'Bearer {refresh_token}'}


def get_detail(content: str) -> str:
    return json.loads(content)['detail']


def get_subject(content: str, token: str) -> str:
    data = json.loads(content)
    auth = AuthJWT()
    jwt = auth.get_raw_jwt(data[token])
    return jwt['sub']
