from app.matching.track_matcher import MatchReason, MatchableTrack, match_track


def test_match_track_prefers_isrc() -> None:
    source = MatchableTrack(
        provider="spotify",
        provider_track_id="sp-1",
        title="Song",
        artist_name="Artist",
        album_name="Album",
        duration_ms=180000,
        isrc="USABC1234567",
    )
    candidates = [
        MatchableTrack(
            provider="apple_music",
            provider_track_id="am-1",
            title="Different",
            artist_name="Someone",
            isrc="USABC1234567",
        )
    ]

    result = match_track(source, candidates)

    assert result.target_track == candidates[0]
    assert result.reason == MatchReason.ISRC_EXACT
    assert result.confidence == 1.0


def test_match_track_uses_title_artist_album() -> None:
    source = MatchableTrack(
        provider="spotify",
        provider_track_id="sp-1",
        title="The Song",
        artist_name="The Artist",
        album_name="The Album",
    )
    candidates = [
        MatchableTrack(
            provider="apple_music",
            provider_track_id="am-1",
            title="the song",
            artist_name="the artist",
            album_name="the album",
        )
    ]

    result = match_track(source, candidates)

    assert result.target_track == candidates[0]
    assert result.reason == MatchReason.TITLE_ARTIST_ALBUM


def test_match_track_uses_duration_fallback() -> None:
    source = MatchableTrack(
        provider="spotify",
        provider_track_id="sp-1",
        title="Song",
        artist_name="Artist",
        duration_ms=200000,
    )
    candidates = [
        MatchableTrack(
            provider="apple_music",
            provider_track_id="am-1",
            title="Song",
            artist_name="Artist",
            duration_ms=202500,
        )
    ]

    result = match_track(source, candidates)

    assert result.target_track == candidates[0]
    assert result.reason == MatchReason.TITLE_ARTIST_DURATION


def test_match_track_uses_normalized_version_title() -> None:
    source = MatchableTrack(
        provider="spotify",
        provider_track_id="sp-1",
        title="Song - 2011 Remastered",
        artist_name="Artist",
    )
    candidates = [
        MatchableTrack(
            provider="apple_music",
            provider_track_id="am-1",
            title="Song",
            artist_name="Artist",
        )
    ]

    result = match_track(source, candidates)

    assert result.target_track == candidates[0]
    assert result.reason == MatchReason.NORMALIZED_VERSION_TITLE


def test_match_track_requires_user_review_when_no_match() -> None:
    source = MatchableTrack(
        provider="spotify",
        provider_track_id="sp-1",
        title="Song",
        artist_name="Artist",
    )
    candidates = [
        MatchableTrack(
            provider="apple_music",
            provider_track_id="am-1",
            title="Other Song",
            artist_name="Other Artist",
        )
    ]

    result = match_track(source, candidates)

    assert result.target_track is None
    assert result.reason == MatchReason.USER_REVIEW_REQUIRED
