# ADR 0001: Do Not Generate or Host Music Audio

## Status

Accepted

## Context

The product idea includes timeline posts for songs, albums, and playlists. A tempting feature is automatically generating part of a song or a preview clip. That creates serious copyright, licensing, provider-policy, and App Store review risk.

Spotify also restricted several Web API features for new use cases on 2024-11-27, including 30-second preview URLs in multi-get responses. Provider preview availability should not be treated as stable infrastructure.

## Decision

The app will not generate, host, cache, upload, or redistribute music audio.

Playback and previews must use official provider functionality only:

- Apple Music through MusicKit / Apple Music API where permitted.
- Spotify through official links, Web API, SDK behavior, and Spotify app playback where permitted.

AI features are limited to text assistance:

- recommendation drafts
- playlist summaries
- tags
- moderation support

## Consequences

Benefits:

- Lower copyright and licensing risk.
- Cleaner App Store review posture.
- Less backend storage and security complexity.
- Better alignment with provider terms.

Tradeoffs:

- Timeline audio previews may be inconsistent across providers.
- Spotify posts may need to rely on opening Spotify instead of inline preview.
- The product must win through recommendation context and playlist recreation, not through embedded audio clips.

