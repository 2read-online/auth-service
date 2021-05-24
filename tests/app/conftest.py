from unittest.mock import Mock

import pytest
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
