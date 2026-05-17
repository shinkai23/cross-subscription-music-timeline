from sqlalchemy.orm import Session

from app.models.track import Track
from app.providers.base import ProviderPlaybackMetadata
from app.repositories.track_repository import TrackRepository


def test_upsert_playback_metadata_creates_track(db_session: Session) -> None:
    repository = TrackRepository(db_session)

    track = repository.upsert_playback_metadata(
        ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="spotify-track-1",
            title="Test Song",
            artist_name="Test Artist",
            album_name="Test Album",
            duration_ms=180000,
            playback_id="spotify-track-1",
            preview_url="https://example.com/preview.mp3",
            artwork_url="https://example.com/artwork.jpg",
            provider_url="https://open.spotify.com/track/spotify-track-1",
            is_playable=True,
            metadata={"explicit": False},
        )
    )

    assert track.id
    assert track.provider == "spotify"
    assert track.provider_track_id == "spotify-track-1"
    assert track.title == "Test Song"
    assert track.artist_name == "Test Artist"
    assert track.album_name == "Test Album"
    assert track.duration_ms == 180000
    assert track.playback_id == "spotify-track-1"
    assert track.preview_url == "https://example.com/preview.mp3"
    assert track.artwork_url == "https://example.com/artwork.jpg"
    assert track.provider_url == "https://open.spotify.com/track/spotify-track-1"
    assert track.is_playable is True
    assert track.provider_metadata == {"explicit": False}
    assert track.metadata_synced_at is not None


def test_upsert_playback_metadata_updates_existing_track(
    db_session: Session,
) -> None:
    repository = TrackRepository(db_session)
    created_track = repository.upsert_playback_metadata(
        ProviderPlaybackMetadata(
            provider="apple_music",
            provider_track_id="apple-track-1",
            title="Old Title",
            artist_name="Old Artist",
            playback_id="apple-track-1",
            is_playable=False,
        )
    )

    updated_track = repository.upsert_playback_metadata(
        ProviderPlaybackMetadata(
            provider="apple_music",
            provider_track_id="apple-track-1",
            title="New Title",
            artist_name="New Artist",
            album_name="New Album",
            duration_ms=210000,
            playback_id="apple-track-1",
            artwork_url="https://example.com/new-artwork.jpg",
            provider_url="https://music.apple.com/song/apple-track-1",
            is_playable=True,
            metadata={"catalog": "us"},
        )
    )

    assert updated_track.id == created_track.id
    assert updated_track.title == "New Title"
    assert updated_track.artist_name == "New Artist"
    assert updated_track.album_name == "New Album"
    assert updated_track.duration_ms == 210000
    assert updated_track.artwork_url == "https://example.com/new-artwork.jpg"
    assert updated_track.provider_url == "https://music.apple.com/song/apple-track-1"
    assert updated_track.is_playable is True
    assert updated_track.provider_metadata == {"catalog": "us"}


def test_list_by_provider_track_ids_returns_empty_dict_for_empty_keys(
    db_session: Session,
) -> None:
    repository = TrackRepository(db_session)

    tracks = repository.list_by_provider_track_ids([])

    assert tracks == {}


def test_list_by_provider_track_ids_returns_matching_tracks(
    db_session: Session,
) -> None:
    repository = TrackRepository(db_session)
    spotify_track = Track(
        provider="spotify",
        provider_track_id="track-1",
        title="Spotify Track",
        artist_name="Spotify Artist",
    )
    apple_music_track = Track(
        provider="apple_music",
        provider_track_id="track-1",
        title="Apple Music Track",
        artist_name="Apple Music Artist",
    )
    extra_track = Track(
        provider="spotify",
        provider_track_id="track-2",
        title="Extra Track",
        artist_name="Extra Artist",
    )
    db_session.add_all([spotify_track, apple_music_track, extra_track])
    db_session.commit()

    tracks = repository.list_by_provider_track_ids(
        [
            ("spotify", "track-1"),
            ("apple_music", "track-1"),
        ]
    )

    assert set(tracks) == {
        ("spotify", "track-1"),
        ("apple_music", "track-1"),
    }
    assert tracks[("spotify", "track-1")].id == spotify_track.id
    assert tracks[("apple_music", "track-1")].id == apple_music_track.id
