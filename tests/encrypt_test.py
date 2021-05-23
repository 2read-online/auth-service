from app.encrypt import hash_password


def test__hash_password():
    hashed_password = hash_password('password')

    assert hashed_password != 'password'
    assert len(hashed_password) == 64
    assert hashed_password != hash_password('another_password')
    assert hashed_password == hash_password('password')
