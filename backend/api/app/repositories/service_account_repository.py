from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service_account import ServiceAccount


class ServiceAccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_provider_user_id(
        self,
        provider: str,
        provider_user_id: str,
    ) -> ServiceAccount | None:
        statement = select(ServiceAccount).where(
            ServiceAccount.provider == provider,
            ServiceAccount.provider_user_id == provider_user_id,
        )
        return self.db.scalar(statement)

    def create_service_account(
        self,
        user_id: str,
        provider: str,
        provider_user_id: str,
        encrypted_refresh_token: str | None = None,
        scopes: str | None = None,
    ) -> ServiceAccount:
        service_account = ServiceAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            encrypted_refresh_token=encrypted_refresh_token,
            scopes=scopes,
        )
        self.db.add(service_account)
        self.db.commit()
        self.db.refresh(service_account)
        return service_account
