from app.services.token_encryption_service import TokenEncryptionService


def test_encrypt_returns_token_for_now() -> None:
    service = TokenEncryptionService()

    encrypted_token = service.encrypt("refresh-token")

    assert encrypted_token == "refresh-token"


def test_encrypt_returns_none_when_token_is_none() -> None:
    service = TokenEncryptionService()

    encrypted_token = service.encrypt(None)

    assert encrypted_token is None


def test_decrypt_returns_encrypted_token_for_now() -> None:
    service = TokenEncryptionService()

    token = service.decrypt("encrypted-refresh-token")

    assert token == "encrypted-refresh-token"


def test_decrypt_returns_none_when_encrypted_token_is_none() -> None:
    service = TokenEncryptionService()

    token = service.decrypt(None)

    assert token is None
