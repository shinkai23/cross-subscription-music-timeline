from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.provider_track import ProviderTrack


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
