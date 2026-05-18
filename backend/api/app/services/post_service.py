from datetime import datetime

from app.models.track import Track
from app.models.user import User
from app.repositories.post_repository import PostRepository
from app.repositories.track_repository import TrackRepository
from app.schemas.post_schema import PostCreate, PostPlaybackRead, PostRead


class PostService:
    def __init__(
        self,
        repository: PostRepository,
        track_repository: TrackRepository,
    ) -> None:
        self.repository = repository
        self.track_repository = track_repository

    def list_posts(
        self,
        limit: int = 50,
        before: datetime | None = None,
    ) -> list[PostRead]:
        posts = self.repository.list_posts(limit=limit, before=before)
        track_keys = [
            (post.source_provider, post.source_item_id)
            for post in posts
        ]

        track_by_key = self.track_repository.list_by_provider_track_ids(track_keys)
        results: list[PostRead] = []
        for post in posts:
            track = track_by_key.get((post.source_provider, post.source_item_id))
            playback = self._build_playback_read(track)

            results.append(
                PostRead(
                    id=post.id,
                    user_id=post.user_id,
                    item_type=post.item_type,
                    source_provider=post.source_provider,
                    source_item_id=post.source_item_id,
                    caption=post.caption,
                    visibility=post.visibility,
                    created_at=post.created_at,
                    playback=playback,
                )
            )

        return results

    def create_post(self, post_in: PostCreate, current_user: User):
        return self.repository.create_post(post_in, user_id=current_user.id)

    def _build_playback_read(self, track: Track | None) -> PostPlaybackRead | None:
        if track is None:
            return None

        return PostPlaybackRead(
            provider=track.provider,
            provider_track_id=track.provider_track_id,
            title=track.title,
            artist_name=track.artist_name,
            album_name=track.album_name,
            duration_ms=track.duration_ms,
            artwork_url=track.artwork_url,
            provider_url=track.provider_url,
            preview_url=track.preview_url,
            playback_id=track.playback_id,
            is_playable=track.is_playable,
        )
