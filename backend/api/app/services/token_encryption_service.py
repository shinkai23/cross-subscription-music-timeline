from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class TokenEncryptionError(Exception):
    pass


class TokenDecryptionError(Exception):
    pass


class TokenEncryptionService:
    def __init__(self, encryption_key: str | None = None) -> None:
        key = encryption_key or get_settings().token_encryption_key
        self.fernet = Fernet(key.encode("utf-8"))

    def encrypt(self, token: str | None) -> str | None:
        if token is None:
            return None

        try:
            return self.fernet.encrypt(token.encode("utf-8")).decode("utf-8")
        except Exception as exc:
            raise TokenEncryptionError() from exc

    def decrypt(self, encrypted_token: str | None) -> str | None:
        if encrypted_token is None:
            return None

        try:
            return self.fernet.decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise TokenDecryptionError() from exc
