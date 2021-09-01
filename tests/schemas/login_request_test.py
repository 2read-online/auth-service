"""Test login request"""
from pydantic import ValidationError
import pytest

from app.schemas import LoginRequest


def test__valid_request():
    """Should pass validation"""
    req = LoginRequest(email='test@test.com', password='pwd')
    assert req


def test__invalid_email():
    """Should raise error if email is invalid"""
    with pytest.raises(ValidationError):
        LoginRequest(email='XXXX', password='pwd')
