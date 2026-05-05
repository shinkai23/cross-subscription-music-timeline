# Provider Integration

## Apple Music

iOS is the primary platform, so Apple Music integration starts with MusicKit.

Initial flow:

1. Request MusicKit authorization in the iOS app.
2. Check Apple Music subscription status.
3. Search the Apple Music catalog.
4. Open Apple Music URLs for songs, albums, and playlists.
5. Create a user's library playlist only after explicit confirmation.

Server responsibility:

- Generate Apple Music developer tokens server-side.
- Keep Apple private keys out of the mobile app.
- Store only the minimum data needed for matching and conversion.

## Spotify

Use OAuth Authorization Code with PKCE for mobile clients.

Initial scopes:

- `playlist-read-private`
- `playlist-modify-private`
- `playlist-modify-public`

Avoid adding broader scopes until a concrete feature requires them.

Initial flow:

1. Mobile client generates a PKCE code verifier and S256 code challenge.
2. Backend builds the Spotify authorize URL with the code challenge.
3. User authorizes with Spotify.
4. App receives the authorization code through redirect URI.
5. Token exchange is implemented with the verifier.
6. Refresh token is stored encrypted if the backend owns long-running playlist operations.

## Cross-Service Matching

Matching should be metadata based:

1. ISRC
2. title + artist + album
3. title + artist + duration
4. user review

Do not use Spotify audio analysis or audio features for new functionality. Do not analyze or store raw audio.

## Playback

Playback must remain provider-owned:

- Apple Music playback through MusicKit where permitted.
- Spotify playback through official app links or SDK behavior.

Inline audio is optional and provider-dependent. The product must still work when no preview is available.
