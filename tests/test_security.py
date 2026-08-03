from datetime import timedelta

import pytest
from jose import ExpiredSignatureError, jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = get_password_hash("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_contains_sub_and_type():
    token = create_access_token(subject="user-1")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "user-1"
    assert payload["type"] == "access"


def test_refresh_token_type():
    token = create_refresh_token(subject="user-1")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["type"] == "refresh"


def test_access_token_respects_expiry_delta():
    token = create_access_token(subject="user-1", expires_delta=timedelta(seconds=-10))
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
