import pytest
from pydantic import ValidationError

from app.schemas import LoginRequest, RegisterRequest


def test__valid_request():
    req = RegisterRequest(email='test@test.com', password='asdf1234', password_confirmation='asdf1234')
    assert req


def test__invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email='test.com', password='asdf1234', password_confirmation='asdf1234')


def test__no_confirmation():
    with pytest.raises(ValidationError):
        RegisterRequest(email='test.com', password='asdf1234')


def test__password_mismatch():
    with pytest.raises(ValidationError):
        RegisterRequest(email='test@test.com', password='asdf1234', password_confirmation='1234asdf')


def test__invalid_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email='test@test.com', password='asd', password_confirmation='asd')
