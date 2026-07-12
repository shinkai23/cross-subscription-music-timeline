from datetime import datetime

from app.models.provider_track import ProviderTrack
from app.models.user import User
from app.repositories.provider_track_repository import ProviderTrackRepository
from app.repositories.post_repository import PostRepository
from app.schemas.post_schema import PostCreate, PostListRead, PostPlaybackRead, PostRead


class ProviderTrackNotFoundError(Exception):
    pass


class PostService:
    def __init__(
        self,
        repository: PostRepository,
        provider_track_repository: ProviderTrackRepository,
    ) -> None:
        self.repository = repository
        self.provider_track_repository = provider_track_repository

    def list_posts(
        self,
        limit: int = 50,
        before: datetime | None = None,
    ) -> PostListRead:
        posts = self.repository.list_posts(limit=limit, before=before)

        provider_track_ids = [
            post.source_provider_track_id
            for post in posts
        ]

        provider_track_by_id = self.provider_track_repository.list_by_ids(
            provider_track_ids
        )

        results: list[PostRead] = []
        for post in posts:
            provider_track = provider_track_by_id.get(post.source_provider_track_id)
            playback = self._build_playback_read(provider_track)

            results.append(
                PostRead(
                    id=post.id,
                    user_id=post.user_id,
                    track_id=post.track_id,
                    source_provider_track_id=post.source_provider_track_id,
                    item_type=post.item_type,
                    caption=post.caption,
                    visibility=post.visibility,
                    created_at=post.created_at,
                    playback=playback,
                )
            )

        return PostListRead(
            items=results,
            next_before=results[-1].created_at if results else None,
        )

    def create_post(self, post_in: PostCreate, current_user: User) -> PostRead:
        provider_track = self.provider_track_repository.get_by_provider_track_id(
            provider=post_in.provider,
            provider_track_id=post_in.provider_track_id,
        )

        if provider_track is None:
            raise ProviderTrackNotFoundError

        post = self.repository.create_post(
            user_id=current_user.id,
            track_id=provider_track.track_id,
            source_provider_track_id=provider_track.id,
            caption=post_in.caption,
            visibility=post_in.visibility,
        )

        return PostRead(
            id=post.id,
            user_id=post.user_id,
            track_id=post.track_id,
            source_provider_track_id=post.source_provider_track_id,
            item_type=post.item_type,
            caption=post.caption,
            visibility=post.visibility,
            created_at=post.created_at,
            playback=self._build_playback_read(provider_track),
        )

    def _build_playback_read(
        self,
        provider_track: ProviderTrack | None,
    ) -> PostPlaybackRead:
        if provider_track is None:
            raise ProviderTrackNotFoundError

        return PostPlaybackRead(
            provider=provider_track.provider,
            provider_track_id=provider_track.provider_track_id,
            title=provider_track.title or "",
            artist_name=provider_track.artist_name or "",
            album_name=provider_track.album_name,
            duration_ms=provider_track.duration_ms,
            artwork_url=provider_track.artwork_url,
            provider_url=provider_track.provider_url,
            preview_url=provider_track.preview_url,
            playback_id=provider_track.playback_id,
            is_playable=provider_track.is_playable,
            playback_mode=self._build_playback_mode(provider_track),
        )

    def _build_playback_mode(self, provider_track: ProviderTrack) -> str:
        if provider_track.provider == "apple_music":
            return "external"

        if provider_track.preview_url:
            return "preview"

        return "external"
