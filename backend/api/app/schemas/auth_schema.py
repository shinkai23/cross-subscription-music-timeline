from pydantic import BaseModel


class DevLoginRequest(BaseModel):
    handle: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
