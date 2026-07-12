from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    display_name: str
    handle: str
    primary_provider: str | None = None


class UserRead(BaseModel):
    id: str
    display_name: str
    handle: str
    primary_provider: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderAccountRead(BaseModel):
    provider: str
    provider_user_id: str
    connected: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderAccountsRead(BaseModel):
    items: list[ProviderAccountRead]
