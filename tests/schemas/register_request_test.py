"""Test user registration request"""
import pytest
from pydantic import ValidationError

from app.schemas import RegisterRequest


def test__valid_request():
    """Should pass validation"""
    req = RegisterRequest(email='test@test.com', password='asdf1234',
                          password_confirmation='asdf1234')
    assert req


def test__invalid_email():
    """Should rise error if email has bad format"""
    with pytest.raises(ValidationError):
        RegisterRequest(email='test.com', password='asdf1234',
                        password_confirmation='asdf1234')


def test__no_confirmation():
    """Should rise error if there is no password confirmation"""
    with pytest.raises(ValidationError):
        RegisterRequest(email='test.com', password='asdf1234')


def test__password_mismatch():
    """Should rise error if password and confirmation mismatch"""
    with pytest.raises(ValidationError):
        RegisterRequest(email='test@test.com', password='asdf1234',
                        password_confirmation='1234asdf')


def test__invalid_password():
    """Should rise error if password is too short"""
    with pytest.raises(ValidationError):
        RegisterRequest(email='test@test.com', password='asd',
                        password_confirmation='asd')
