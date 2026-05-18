from pydantic import BaseModel, Field

from app.providers.base import ProviderPlaybackMetadata


class AddTracksToPlaylistRequest(BaseModel):
    track_ids: list[str] = Field(min_length=1)


class ProviderPlaybackRead(ProviderPlaybackMetadata):
    track_id: str | None = None
    provider_track_row_id: str | None = None