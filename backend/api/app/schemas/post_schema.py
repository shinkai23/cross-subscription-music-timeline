from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    item_type: str
    source_provider: str
    source_item_id: str
    caption: str | None = None
    visibility: str = "public"


class PostPlaybackRead(BaseModel):
    provider: str
    provider_track_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    artwork_url: str | None = None
    provider_url: str | None = None
    preview_url: str | None = None
    playback_id: str | None = None
    is_playable: bool


class PostRead(BaseModel):
    id: str
    user_id: str
    item_type: str
    source_provider: str
    source_item_id: str
    caption: str | None
    visibility: str
    created_at: datetime
    playback: PostPlaybackRead | None = None

    model_config = ConfigDict(from_attributes=True)


class PostListRead(BaseModel):
    items: list[PostRead]
    next_before: datetime | None = None
