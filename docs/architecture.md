# Architecture

## System Overview

```text
iOS App
  SwiftUI
  MusicKit
  Service auth UI
  Timeline and playlist review

Android App
  Jetpack Compose
  Service auth UI
  Timeline and playlist review

Backend API
  Auth/session
  Posts
  Timeline
  Track metadata
  Playlist conversion
  Moderation

Workers
  Metadata refresh
  Cross-service matching
  Conversion result analysis

Database
  PostgreSQL
```

## Backend Modules

- `auth`: app sessions and provider account linking
- `providers`: Apple Music and Spotify adapters
- `catalog`: normalized track, album, artist, and playlist metadata
- `posts`: user posts and timeline queries
- `matching`: cross-service track matching
- `conversion`: target playlist creation
- `moderation`: reports, takedowns, blocks
- `ai`: text-only caption/tag assistance

## Provider Adapter Interface

```ts
type Provider = "apple_music" | "spotify";

interface MusicProviderAdapter {
  provider: Provider;
  searchTracks(query: TrackSearchQuery): Promise<ProviderTrack[]>;
  getPlaylist(id: string, userToken?: string): Promise<ProviderPlaylist>;
  createPlaylist(input: CreatePlaylistInput, userToken: string): Promise<CreatedPlaylist>;
  addTracksToPlaylist(input: AddTracksInput, userToken: string): Promise<void>;
  buildOpenUrl(item: ProviderItemRef): string;
}
```

## Matching Strategy

Priority:

1. ISRC exact match
2. title + primary artist + album
3. title + primary artist + duration tolerance
4. normalized title without version suffixes
5. user-selected candidate

Track matching must store confidence and reason:

```text
track_matches
  source_provider
  source_track_id
  target_provider
  target_track_id
  confidence
  reason
  created_at
```

## Data Model Draft

```text
users
  id
  display_name
  handle
  primary_provider
  created_at

service_accounts
  id
  user_id
  provider
  provider_user_id
  encrypted_refresh_token
  scopes
  disconnected_at

posts
  id
  user_id
  item_type
  source_provider
  source_item_id
  caption
  visibility
  created_at

tracks
  id
  provider
  provider_track_id
  isrc
  title
  artist_name
  album_name
  duration_ms
  artwork_url
  provider_url

playlists
  id
  provider
  provider_playlist_id
  title
  description
  owner_display_name
  provider_url

playlist_items
  playlist_id
  position
  track_id

reports
  id
  reporter_user_id
  target_type
  target_id
  reason
  status
```

## iOS First Plan

Use SwiftUI and MusicKit first because Apple Music is the priority and iOS provides the strongest native integration.

Initial iOS screens:

- service selection
- Apple Music authorization
- timeline
- post composer
- playlist conversion review
- profile
- report sheet

## Security

- Store provider tokens encrypted on backend.
- Use PKCE for Spotify mobile auth.
- Keep Apple private key server-side only.
- Use short-lived app sessions.
- Scope provider permissions narrowly.
- Add account disconnect and token revocation/deletion path.

