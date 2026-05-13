import pytest

from app.services.token_encryption_service import (
    TokenDecryptionError,
    TokenEncryptionService,
)

TEST_ENCRYPTION_KEY = "3QUlaYLveO5FK5fWDYTA7O7um9OzDCV4u2NA-ZXq9a0="


def test_encrypt_returns_encrypted_token() -> None:
    service = TokenEncryptionService(encryption_key=TEST_ENCRYPTION_KEY)

    encrypted_token = service.encrypt("refresh-token")

    assert encrypted_token is not None
    assert encrypted_token != "refresh-token"


def test_encrypt_returns_none_when_token_is_none() -> None:
    service = TokenEncryptionService(encryption_key=TEST_ENCRYPTION_KEY)

    encrypted_token = service.encrypt(None)

    assert encrypted_token is None


def test_decrypt_returns_original_token() -> None:
    service = TokenEncryptionService(encryption_key=TEST_ENCRYPTION_KEY)

    encrypted_token = service.encrypt("refresh-token")
    token = service.decrypt(encrypted_token)

    assert token == "refresh-token"


def test_decrypt_returns_none_when_encrypted_token_is_none() -> None:
    service = TokenEncryptionService(encryption_key=TEST_ENCRYPTION_KEY)

    token = service.decrypt(None)

    assert token is None


def test_decrypt_raises_when_token_is_invalid() -> None:
    service = TokenEncryptionService(encryption_key=TEST_ENCRYPTION_KEY)

    with pytest.raises(TokenDecryptionError):
        service.decrypt("invalid-token")
