from pydantic import BaseModel, Field


class AppleMusicConnectRequest(BaseModel):
    provider_user_id: str = Field(min_length=1)
    music_user_token: str = Field(min_length=1)


class AppleMusicConnectResponse(BaseModel):
    provider: str
    connected: bool
