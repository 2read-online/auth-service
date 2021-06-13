# pylint: disable=redefined-outer-name
"""Test token refreshing"""
from tests.app.conftest import get_detail, get_subject


def test__refresh_token_ok(client, user_id, headers):
    """Should refresh access token
    """
    resp = client.get('/auth/refresh', headers=headers)
    assert resp.status_code == 200
    assert get_subject(resp.content, 'access_token') == str(user_id)


def test__refresh_token_no_access(client):
    """Should not refresh access token if there is no refresh token
    """
    resp = client.get('/auth/refresh', headers={})
    assert resp.status_code == 401
    assert get_detail(resp.content) == 'Missing Authorization Header'
