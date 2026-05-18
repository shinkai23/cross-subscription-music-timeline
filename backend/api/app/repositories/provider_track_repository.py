from datetime import datetime, timezone

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.models.provider_track import ProviderTrack
from app.providers.base import ProviderPlaybackMetadata


class ProviderTrackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_provider_track_id(
        self,
        provider: str,
        provider_track_id: str,
    ) -> ProviderTrack | None:
        statement = select(ProviderTrack).where(
            ProviderTrack.provider == provider,
            ProviderTrack.provider_track_id == provider_track_id,
        )
        return self.db.scalar(statement)

    def list_by_track_id(self, track_id: str) -> list[ProviderTrack]:
        statement = select(ProviderTrack).where(
            ProviderTrack.track_id == track_id,
        )
        return list(self.db.scalars(statement).all())

    def list_by_ids(self, ids: list[str]) -> dict[str, ProviderTrack]:
        if not ids:
            return {}

        statement = select(ProviderTrack).where(ProviderTrack.id.in_(ids))
        provider_tracks = self.db.scalars(statement).all()

        return {
            provider_track.id: provider_track
            for provider_track in provider_tracks
        }

    def list_by_provider_track_ids(
        self,
        keys: list[tuple[str, str]],
    ) -> dict[tuple[str, str], ProviderTrack]:
        if not keys:
            return {}

        statement = select(ProviderTrack).where(
            tuple_(ProviderTrack.provider, ProviderTrack.provider_track_id).in_(keys)
        )

        provider_tracks = self.db.scalars(statement).all()

        return {
            (provider_track.provider, provider_track.provider_track_id): provider_track
            for provider_track in provider_tracks
        }

    def list_by_track_ids_and_provider(
        self,
        track_ids: list[str],
        provider: str,
    ) -> dict[str, ProviderTrack]:
        if not track_ids:
            return {}

        statement = select(ProviderTrack).where(
            ProviderTrack.track_id.in_(track_ids),
            ProviderTrack.provider == provider,
        )
        provider_tracks = self.db.scalars(statement).all()

        return {
            provider_track.track_id: provider_track
            for provider_track in provider_tracks
        }

    def upsert_playback_metadata(
        self,
        track_id: str,
        playback: ProviderPlaybackMetadata,
    ) -> ProviderTrack:
        provider_track = self.get_by_provider_track_id(
            provider=playback.provider,
            provider_track_id=playback.provider_track_id,
        )
        if provider_track is None:
            provider_track = ProviderTrack(
                track_id=track_id,
                provider=playback.provider,
                provider_track_id=playback.provider_track_id,
            )
            self.db.add(provider_track)

        provider_track.title = playback.title
        provider_track.artist_name = playback.artist_name
        provider_track.album_name = playback.album_name
        provider_track.duration_ms = playback.duration_ms
        provider_track.playback_id = playback.playback_id
        provider_track.preview_url = playback.preview_url
        provider_track.artwork_url = playback.artwork_url
        provider_track.provider_url = playback.provider_url
        provider_track.is_playable = playback.is_playable
        provider_track.playback_source = "preview_url" if playback.preview_url else None
        provider_track.provider_metadata = playback.metadata
        provider_track.isrc = playback.isrc
        provider_track.metadata_synced_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(provider_track)
        return provider_track
