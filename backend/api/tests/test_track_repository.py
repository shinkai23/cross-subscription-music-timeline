from sqlalchemy.orm import Session

from app.models.track import Track
from app.providers.base import ProviderPlaybackMetadata
from app.repositories.track_repository import TrackRepository


def test_get_or_create_from_playback_returns_existing_track_by_isrc(
    db_session: Session,
) -> None:
    existing_track = Track(
        isrc="USABC1234567",
        title="Existing Track",
        artist_name="Existing Artist",
    )
    db_session.add(existing_track)
    db_session.commit()
    repository = TrackRepository(db_session)

    track = repository.get_or_create_from_playback(
        ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="spotify-track-1",
            title="Spotify Track",
            artist_name="Spotify Artist",
            isrc="USABC1234567",
            playback_id="spotify-track-1",
        )
    )

    assert track.id == existing_track.id


def test_get_or_create_from_playback_creates_track_when_isrc_missing(
    db_session: Session,
) -> None:
    repository = TrackRepository(db_session)

    track = repository.get_or_create_from_playback(
        ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="spotify-track-1",
            title="Spotify Track",
            artist_name="Spotify Artist",
            album_name="Spotify Album",
            duration_ms=180000,
            playback_id="spotify-track-1",
            artwork_url="https://example.com/artwork.jpg",
            provider_url="https://open.spotify.com/track/spotify-track-1",
        )
    )

    assert track.id
    assert track.isrc is None
    assert track.title == "Spotify Track"
    assert track.artist_name == "Spotify Artist"
    assert track.album_name == "Spotify Album"
    assert track.duration_ms == 180000
    assert track.artwork_url == "https://example.com/artwork.jpg"
    assert track.canonical_source == "spotify"
