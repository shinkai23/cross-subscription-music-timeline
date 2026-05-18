from sqlalchemy.orm import Session

from app.models.provider_track import ProviderTrack
from app.models.track import Track
from app.repositories.provider_track_repository import ProviderTrackRepository


def test_get_by_provider_track_id(db_session: Session) -> None:
    track = Track(
        provider="spotify",
        provider_track_id="spotify-track-1",
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
        provider="spotify",
        provider_track_id="spotify-track-1",
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


def test_list_by_track_ids_and_provider(db_session: Session) -> None:
    track_1 = Track(
        provider="spotify",
        provider_track_id="spotify-track-1",
        title="Canonical Track 1",
        artist_name="Canonical Artist",
    )
    track_2 = Track(
        provider="apple_music",
        provider_track_id="apple-track-2",
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
