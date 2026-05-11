from pydantic import BaseModel


class SpotifyAuthorizationResponse(BaseModel):
    authorization_url: str
    state: str
    code_verifier: str


class SpotifyCallbackResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None


class SpotifyTokenExchangeRequest(BaseModel):
    code: str
    code_verifier: str


class SpotifyTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str | None = None
    scope: str | None = None
