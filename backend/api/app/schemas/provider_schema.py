from pydantic import BaseModel, Field


class AddTracksToPlaylistRequest(BaseModel):
    track_ids: list[str] = Field(min_length=1)
