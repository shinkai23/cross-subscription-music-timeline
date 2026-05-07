from datetime import timedelta

import pytest

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_create_and_decode_access_token() -> None:
    token = create_access_token(
        subject="user-1",
        extra_claims={"scope": "test"},
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["scope"] == "test"
    assert "exp" in payload


def test_expired_access_token_is_invalid() -> None:
    token = create_access_token(
        subject="user-1",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_invalid_access_token_is_rejected() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("invalid-token")


def test_password_hash_and_verify() -> None:
    hashed_password = hash_password("plain-password")

    assert hashed_password != "plain-password"
    assert verify_password("plain-password", hashed_password)
    assert not verify_password("wrong-password", hashed_password)
