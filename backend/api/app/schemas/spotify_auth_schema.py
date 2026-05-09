from pydantic import BaseModel


class SpotifyAuthorizationResponse(BaseModel):
    authorization_url: str
    state: str
    code_verifier: str
