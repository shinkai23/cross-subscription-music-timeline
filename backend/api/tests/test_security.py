from datetime import timedelta

import pytest

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plain_password() -> None:
    hashed_password = hash_password("plain-password")

    assert hashed_password != "plain-password"


def test_verify_password_accepts_correct_password() -> None:
    hashed_password = hash_password("plain-password")

    assert verify_password("plain-password", hashed_password)


def test_verify_password_rejects_wrong_password() -> None:
    hashed_password = hash_password("plain-password")

    assert not verify_password("wrong-password", hashed_password)


def test_create_access_token_includes_subject_and_extra_claims() -> None:
    token = create_access_token(
        subject="user-1",
        extra_claims={"scope": "test"},
    )
    payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["scope"] == "test"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_access_token_rejects_invalid_token() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("invalid-token")


def test_decode_access_token_rejects_expired_token() -> None:
    token = create_access_token(
        subject="user-1",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
