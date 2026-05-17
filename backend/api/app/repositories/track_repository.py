from datetime import datetime, timezone

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.models.track import Track
from app.providers.base import ProviderPlaybackMetadata


class TrackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_provider_track_id(
        self,
        provider: str,
        provider_track_id: str,
    ) -> Track | None:
        statement = select(Track).where(
            Track.provider == provider,
            Track.provider_track_id == provider_track_id,
        )

        return self.db.scalar(statement)

    def list_by_provider_track_ids(
        self,
        keys: list[tuple[str, str]],
    ) -> dict[tuple[str, str], Track]:
        if not keys:
            return {}

        statement = select(Track).where(
            tuple_(Track.provider, Track.provider_track_id).in_(keys)
        )

        tracks = self.db.scalars(statement).all()

        return {
            (track.provider, track.provider_track_id): track
            for track in tracks
        }

    def upsert_playback_metadata(
        self,
        playback: ProviderPlaybackMetadata,
    ) -> Track:
        track = self.get_by_provider_track_id(
            provider=playback.provider,
            provider_track_id=playback.provider_track_id,
        )
        if track is None:
            track = Track(
                provider=playback.provider,
                provider_track_id=playback.provider_track_id,
                title=playback.title,
                artist_name=playback.artist_name,
            )
            self.db.add(track)

        track.title = playback.title
        track.artist_name = playback.artist_name
        track.album_name = playback.album_name
        track.duration_ms = playback.duration_ms
        track.artwork_url = playback.artwork_url
        track.provider_url = playback.provider_url
        track.preview_url = playback.preview_url
        track.playback_id = playback.playback_id
        track.is_playable = playback.is_playable
        track.provider_metadata = playback.metadata
        track.metadata_synced_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(track)
        return track
