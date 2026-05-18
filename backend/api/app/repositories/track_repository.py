from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.track import Track
from app.providers.base import ProviderPlaybackMetadata


class TrackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_isrc(self, isrc: str) -> Track | None:
        statement = select(Track).where(Track.isrc == isrc)
        return self.db.scalar(statement)

    def get_or_create_from_playback(
        self,
        playback: ProviderPlaybackMetadata,
    ) -> Track:
        track = None

        if playback.isrc is not None:
            track = self.get_by_isrc(playback.isrc)

        if track is None:
            track = Track(
                isrc=playback.isrc,
                title=playback.title,
                artist_name=playback.artist_name,
                album_name=playback.album_name,
                duration_ms=playback.duration_ms,
                artwork_url=playback.artwork_url,
                canonical_source=playback.provider,
            )
            self.db.add(track)

        self.db.commit()
        self.db.refresh(track)
        return track
