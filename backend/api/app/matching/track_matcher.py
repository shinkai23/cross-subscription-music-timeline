import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class MatchReason(str, Enum):
    ISRC_EXACT = "isrc_exact"
    TITLE_ARTIST_ALBUM = "title_artist_album"
    TITLE_ARTIST_DURATION = "title_artist_duration"
    NORMALIZED_VERSION_TITLE = "normalized_version_title"
    USER_REVIEW_REQUIRED = "user_review_required"


@dataclass(frozen=True)
class MatchableTrack:
    provider: str
    provider_track_id: str
    title: str
    artist_name: str
    album_name: str | None = None
    duration_ms: int | None = None
    isrc: str | None = None


@dataclass(frozen=True)
class TrackMatchResult:
    target_track: MatchableTrack | None
    confidence: float
    reason: MatchReason


def match_track(source: MatchableTrack, candidates: list[MatchableTrack]) -> TrackMatchResult:
    exact_isrc = _find(candidates, lambda track: _same_isrc(source, track))
    if exact_isrc:
        return TrackMatchResult(exact_isrc, 1.0, MatchReason.ISRC_EXACT)

    title_artist_album = _find(
        candidates,
        lambda track: _same_title_artist(source, track) and _same_album(source, track),
    )
    if title_artist_album:
        return TrackMatchResult(title_artist_album, 0.92, MatchReason.TITLE_ARTIST_ALBUM)

    title_artist_duration = _find(
        candidates,
        lambda track: _same_title_artist(source, track) and _duration_close(source, track),
    )
    if title_artist_duration:
        return TrackMatchResult(title_artist_duration, 0.84, MatchReason.TITLE_ARTIST_DURATION)

    normalized_version_title = _find(
        candidates,
        lambda track: _normalize_version_title(source.title) == _normalize_version_title(track.title)
        and _normalize_text(source.artist_name) == _normalize_text(track.artist_name),
    )
    if normalized_version_title:
        return TrackMatchResult(
            normalized_version_title,
            0.7,
            MatchReason.NORMALIZED_VERSION_TITLE,
        )

    return TrackMatchResult(None, 0.0, MatchReason.USER_REVIEW_REQUIRED)


def _find(candidates: list[MatchableTrack], predicate) -> MatchableTrack | None:
    return next((candidate for candidate in candidates if predicate(candidate)), None)


def _same_isrc(source: MatchableTrack, candidate: MatchableTrack) -> bool:
    return bool(source.isrc and candidate.isrc and source.isrc.upper() == candidate.isrc.upper())


def _same_title_artist(source: MatchableTrack, candidate: MatchableTrack) -> bool:
    return (
        _normalize_text(source.title) == _normalize_text(candidate.title)
        and _normalize_text(source.artist_name) == _normalize_text(candidate.artist_name)
    )


def _same_album(source: MatchableTrack, candidate: MatchableTrack) -> bool:
    return bool(
        source.album_name
        and candidate.album_name
        and _normalize_text(source.album_name) == _normalize_text(candidate.album_name)
    )


def _duration_close(source: MatchableTrack, candidate: MatchableTrack, tolerance_ms: int = 3000) -> bool:
    if source.duration_ms is None or candidate.duration_ms is None:
        return False
    return abs(source.duration_ms - candidate.duration_ms) <= tolerance_ms


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = re.sub(r"&", " and ", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_version_title(value: str) -> str:
    normalized = _normalize_text(value)
    normalized = re.sub(
        r"\b(remaster(?:ed)?|mono|stereo|explicit|clean|deluxe|bonus track|radio edit|edit)\b",
        " ",
        normalized,
    )
    normalized = re.sub(r"\b(19|20)\d{2}\b", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()
