from sqlalchemy.orm import Session

from app.models.provider_track import ProviderTrack
from app.models.track import Track
from app.providers.base import ProviderPlaybackMetadata
from app.repositories.provider_track_repository import ProviderTrackRepository


def test_get_by_provider_track_id(db_session: Session) -> None:
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="Spotify Track",
        artist_name="Spotify Artist",
    )
    db_session.add_all([track, provider_track])
    db_session.commit()
    repository = ProviderTrackRepository(db_session)

    found_provider_track = repository.get_by_provider_track_id(
        provider="spotify",
        provider_track_id="spotify-track-1",
    )

    assert found_provider_track is not None
    assert found_provider_track.id == provider_track.id


def test_list_by_track_id(db_session: Session) -> None:
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    spotify_provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="spotify-track-1",
    )
    apple_music_provider_track = ProviderTrack(
        track=track,
        provider="apple_music",
        provider_track_id="apple-track-1",
    )
    db_session.add_all([track, spotify_provider_track, apple_music_provider_track])
    db_session.commit()
    repository = ProviderTrackRepository(db_session)

    provider_tracks = repository.list_by_track_id(track.id)

    assert {provider_track.id for provider_track in provider_tracks} == {
        spotify_provider_track.id,
        apple_music_provider_track.id,
    }


def test_list_by_provider_track_ids_returns_empty_dict_for_empty_keys(
    db_session: Session,
) -> None:
    repository = ProviderTrackRepository(db_session)

    provider_tracks = repository.list_by_provider_track_ids([])

    assert provider_tracks == {}


def test_list_by_provider_track_ids_returns_matching_provider_tracks(
    db_session: Session,
) -> None:
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    spotify_provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="track-1",
    )
    apple_music_provider_track = ProviderTrack(
        track=track,
        provider="apple_music",
        provider_track_id="track-1",
    )
    extra_provider_track = ProviderTrack(
        track=track,
        provider="spotify",
        provider_track_id="track-2",
    )
    db_session.add_all(
        [
            track,
            spotify_provider_track,
            apple_music_provider_track,
            extra_provider_track,
        ]
    )
    db_session.commit()
    repository = ProviderTrackRepository(db_session)

    provider_tracks = repository.list_by_provider_track_ids(
        [
            ("spotify", "track-1"),
            ("apple_music", "track-1"),
        ]
    )

    assert set(provider_tracks) == {
        ("spotify", "track-1"),
        ("apple_music", "track-1"),
    }
    assert provider_tracks[("spotify", "track-1")].id == spotify_provider_track.id
    assert (
        provider_tracks[("apple_music", "track-1")].id
        == apple_music_provider_track.id
    )


def test_list_by_track_ids_and_provider(db_session: Session) -> None:
    track_1 = Track(
        title="Canonical Track 1",
        artist_name="Canonical Artist",
    )
    track_2 = Track(
        title="Canonical Track 2",
        artist_name="Canonical Artist",
    )
    spotify_provider_track = ProviderTrack(
        track=track_1,
        provider="spotify",
        provider_track_id="spotify-track-1",
    )
    apple_music_provider_track = ProviderTrack(
        track=track_2,
        provider="apple_music",
        provider_track_id="apple-track-2",
    )
    db_session.add_all(
        [
            track_1,
            track_2,
            spotify_provider_track,
            apple_music_provider_track,
        ]
    )
    db_session.commit()
    repository = ProviderTrackRepository(db_session)

    provider_tracks = repository.list_by_track_ids_and_provider(
        track_ids=[track_1.id, track_2.id],
        provider="spotify",
    )

    assert set(provider_tracks) == {track_1.id}
    assert provider_tracks[track_1.id].id == spotify_provider_track.id


def test_upsert_playback_metadata_creates_provider_track(
    db_session: Session,
) -> None:
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    db_session.add(track)
    db_session.commit()
    repository = ProviderTrackRepository(db_session)

    provider_track = repository.upsert_playback_metadata(
        track_id=track.id,
        playback=ProviderPlaybackMetadata(
            provider="spotify",
            provider_track_id="spotify-track-1",
            title="Spotify Track",
            artist_name="Spotify Artist",
            album_name="Spotify Album",
            duration_ms=180000,
            isrc="GBDUW0000053",
            metadata={"explicit": False},
            playback_id="spotify-track-1",
            preview_url="https://example.com/preview.mp3",
            artwork_url="https://example.com/artwork.jpg",
            provider_url="https://open.spotify.com/track/spotify-track-1",
            is_playable=True,
        ),
    )

    assert provider_track.track_id == track.id
    assert provider_track.provider == "spotify"
    assert provider_track.provider_track_id == "spotify-track-1"
    assert provider_track.title == "Spotify Track"
    assert provider_track.artist_name == "Spotify Artist"
    assert provider_track.album_name == "Spotify Album"
    assert provider_track.duration_ms == 180000
    assert provider_track.isrc == "GBDUW0000053"
    assert provider_track.provider_metadata == {"explicit": False}
    assert provider_track.playback_id == "spotify-track-1"
    assert provider_track.preview_url == "https://example.com/preview.mp3"
    assert provider_track.artwork_url == "https://example.com/artwork.jpg"
    assert provider_track.provider_url == "https://open.spotify.com/track/spotify-track-1"
    assert provider_track.is_playable is True
    assert provider_track.playback_source == "preview_url"
    assert provider_track.metadata_synced_at is not None


def test_upsert_playback_metadata_updates_existing_provider_track(
    db_session: Session,
) -> None:
    track = Track(
        title="Canonical Track",
        artist_name="Canonical Artist",
    )
    db_session.add(track)
    db_session.commit()
    repository = ProviderTrackRepository(db_session)
    created_provider_track = repository.upsert_playback_metadata(
        track_id=track.id,
        playback=ProviderPlaybackMetadata(
            provider="apple_music",
            provider_track_id="apple-track-1",
            title="Old Title",
            artist_name="Old Artist",
            playback_id="apple-track-1",
            is_playable=False,
        ),
    )

    updated_provider_track = repository.upsert_playback_metadata(
        track_id=track.id,
        playback=ProviderPlaybackMetadata(
            provider="apple_music",
            provider_track_id="apple-track-1",
            title="New Title",
            artist_name="New Artist",
            playback_id="apple-track-1",
            preview_url="https://example.com/apple-preview.m4a",
            is_playable=True,
        ),
    )

    assert updated_provider_track.id == created_provider_track.id
    assert updated_provider_track.title == "New Title"
    assert updated_provider_track.artist_name == "New Artist"
    assert updated_provider_track.preview_url == "https://example.com/apple-preview.m4a"
    assert updated_provider_track.is_playable is True
    assert updated_provider_track.playback_source == "preview_url"
