import pytest
from pydantic import ValidationError

from app.schemas import LoginRequest


def test__valid_request():
    req = LoginRequest(email='test@test.com', password='pwd')
    assert req


def test__invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email='XXXX', password='pwd')


def test_invalid_pwd():
    with pytest.raises(ValidationError):
        LoginRequest(email='test@test.com', password='')
