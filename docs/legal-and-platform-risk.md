# Legal and Platform Risk

This document is an engineering risk checklist, not legal advice. Before public launch, confirm with current Apple and Spotify terms and, if possible, a qualified lawyer.

## Core Policy

The app must treat streaming providers as the source of truth for playback and metadata. It should not host, redistribute, generate, or cache music audio.

## High-Risk Areas

### Audio Clips

Do not generate song clips. Do not store preview audio. Do not bypass provider restrictions with third-party audio sources.

Apple Music song resources may include preview assets. Use only official URLs and only in the way Apple permits.

Spotify preview access is not reliable for new development. Spotify announced on 2024-11-27 that new Web API use cases no longer have access to several endpoints and functionality, including 30-second preview URLs in multi-get responses. Design the app without depending on Spotify previews.

### Lyrics

Do not support full lyric posting. If short quotes are allowed in the future, keep them short, user-entered, attributed where needed, and removable through moderation.

### Artwork and Metadata

Use cover art and metadata only with the required attribution and link-back behavior for each provider. Do not sell metadata or artwork as a standalone product.

Spotify policy states that metadata, cover art, and Audio Preview Clips must be accompanied by a link back to applicable Spotify content. Build link-back into the component design rather than relying on manual UI decisions.

### Playlist Transfer

The safest product framing is user-directed metadata transfer:

- A user chooses to post or import playlist metadata.
- A receiving user explicitly chooses to recreate a playlist.
- The app shows matched and unmatched tracks before writing to the user's library.

Avoid:

- scraping private playlists
- silently copying playlists
- copying local files
- claiming perfect conversion

### AI

Do not use Spotify Content, Apple Music content, audio previews, artwork, or service-derived content to train a model.

AI should work from:

- user-written text
- track titles
- artist names
- album names
- genres when API terms allow display/use

### Privacy

Only request scopes required for the visible task. Provide account disconnect and data deletion flows.

Store:

- provider account id
- provider type
- encrypted refresh tokens where needed
- granted scopes
- timestamps

Do not store:

- raw music audio
- full private library snapshots unless needed and explicitly explained
- unnecessary listening history

## Provider Notes

### Apple Music

Apple Music / MusicKit can support playback, library access, playlist creation, and catalog lookup after user authorization. Developer tokens must be handled securely and should not expose private keys in the client.

### Spotify

Use OAuth Authorization Code with PKCE for mobile clients. Spotify iOS SDK playback control depends on the Spotify app, and on-demand track URI playback requires Premium. New apps should not rely on restricted endpoints such as audio analysis, audio features, recommendations, or preview URLs.

## Moderation Requirements

- Report post
- Hide post
- Delete own post
- Block user
- Admin takedown
- Copyright complaint category
- Audit log for moderation decisions

## Launch Gate

Before App Store or public beta:

1. Re-check Apple Music API, MusicKit, Spotify Developer Terms, Spotify Developer Policy.
2. Verify all metadata cards show required attribution and links.
3. Verify disconnect and deletion flows.
4. Verify no raw audio is persisted.
5. Verify AI prompts cannot request soundalike audio or full lyrics.

