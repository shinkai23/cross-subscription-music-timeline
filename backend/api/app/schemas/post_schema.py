from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    item_type: str
    source_provider: str
    source_item_id: str
    caption: str | None = None
    visibility: str = "public"


class PostRead(BaseModel):
    id: str
    user_id: str
    item_type: str
    source_provider: str
    source_item_id: str
    caption: str | None
    visibility: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
