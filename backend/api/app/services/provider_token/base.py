from abc import ABC, abstractmethod

from app.models.service_account import ServiceAccount


class ProviderTokenService(ABC):
    provider: str

    @abstractmethod
    async def get_access_token(self, service_account: ServiceAccount) -> str:
        raise NotImplementedError