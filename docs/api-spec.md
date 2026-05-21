# API仕様書

## 共通

Base URL:

```text
http://localhost:4000
```

認証が必要なAPIでは、以下のヘッダーを付ける。

```http
Authorization: Bearer <JWT>
```

レスポンスはJSON。

## Health

### GET /health

ヘルスチェック。

Headers:

```http
なし
```

Response:

```json
{
  "status": "ok"
}
```

## Users

### POST /users

ユーザーを作成する。

Headers:

```http
Content-Type: application/json
```

Body:

```json
{
  "display_name": "Sinkai",
  "handle": "sinkaii",
  "primary_provider": "spotify"
}
```

Response `201`:

```json
{
  "id": "user-id",
  "display_name": "Sinkai",
  "handle": "sinkaii",
  "primary_provider": "spotify",
  "created_at": "2026-05-20T00:00:00"
}
```

Error:

- `409`: handleが重複している

### GET /me

現在のユーザーを取得する。

Headers:

```http
Authorization: Bearer <JWT>
```

Response `200`:

```json
{
  "id": "user-id",
  "display_name": "Sinkai",
  "handle": "sinkaii",
  "primary_provider": "spotify",
  "created_at": "2026-05-20T00:00:00"
}
```

Error:

- `401`: JWTが無効

## Spotify Auth

### GET /auth/spotify/authorize

Spotify OAuth PKCE用の認可URL、state、code verifierを生成する。

Headers:

```http
なし
```

Response `200`:

```json
{
  "authorization_url": "https://accounts.spotify.com/authorize?...",
  "state": "random-state",
  "code_verifier": "random-code-verifier"
}
```

### GET /auth/spotify/callback

Spotify callbackの検証とtoken exchangeを行う。

Query:

```text
code=spotify-code
state=actual-state
expected_state=expected-state
code_verifier=code-verifier
```

Response `200`:

```json
{
  "access_token": "access-token",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh-token",
  "scope": "user-read-email"
}
```

Error:

- `400`: stateが不正
- `502`: Spotify token exchangeに失敗

### POST /auth/spotify/connect

Spotifyアカウントを現在のユーザーに連携する。

Headers:

```http
Authorization: Bearer <JWT>
Content-Type: application/json
```

Body:

```json
{
  "code": "spotify-code",
  "code_verifier": "code-verifier",
  "state": "actual-state",
  "expected_state": "expected-state"
}
```

Response `200`:

```json
{
  "provider": "spotify",
  "provider_user_id": "spotify-user-id"
}
```

Error:

- `400`: stateが不正
- `401`: JWTが無効
- `409`: すでに連携済み
- `502`: Spotify API連携に失敗

## Apple Music Auth

### POST /auth/apple-music/connect

Apple Musicアカウントを現在のユーザーに連携する。

Headers:

```http
Authorization: Bearer <JWT>
Content-Type: application/json
```

Body:

```json
{
  "provider_user_id": "apple-music-user-id",
  "music_user_token": "music-user-token"
}
```

Response `200`:

```json
{
  "provider": "apple_music",
  "connected": true
}
```

Error:

- `401`: JWTが無効
- `409`: すでに連携済み

## Providers

Provider APIは認証済みユーザーの連携済みアカウントを使う。

`provider` には以下を指定する。

- `spotify`
- `apple_music`

### GET /providers/{provider}/search/tracks

曲を検索する。

Headers:

```http
Authorization: Bearer <JWT>
```

Query:

```text
q=search keyword
```

Response `200`:

```json
[
  {
    "provider": "spotify",
    "provider_track_id": "spotify-track-id",
    "title": "Track Title",
    "artist_name": "Artist Name",
    "album_name": "Album Name",
    "duration_ms": 180000,
    "isrc": "JPXXX0000000",
    "provider_url": "https://open.spotify.com/track/..."
  }
]
```

Error:

- `401`: JWTが無効
- `409`: Providerアカウントが未連携

### GET /providers/{provider}/tracks/{track_id}/playback

Provider上の曲IDから、タイムライン再生に必要なメタデータを取得し、DBに保存する。

Headers:

```http
Authorization: Bearer <JWT>
```

Response `200`:

```json
{
  "provider": "spotify",
  "provider_track_id": "spotify-track-id",
  "title": "Track Title",
  "artist_name": "Artist Name",
  "album_name": "Album Name",
  "duration_ms": 180000,
  "isrc": "JPXXX0000000",
  "metadata": {},
  "playback_id": "spotify-track-id",
  "preview_url": null,
  "artwork_url": "https://...",
  "provider_url": "https://open.spotify.com/track/...",
  "is_playable": true,
  "track_id": "canonical-track-id",
  "provider_track_row_id": "provider-track-row-id"
}
```

Error:

- `401`: JWTが無効
- `409`: Providerアカウントが未連携
- `502`: Provider API連携に失敗

### GET /providers/{provider}/playlists/{playlist_id}

Provider上のプレイリストを取得する。

Headers:

```http
Authorization: Bearer <JWT>
```

Response `200`:

```json
{
  "provider": "spotify",
  "provider_playlist_id": "playlist-id",
  "title": "Playlist Title",
  "tracks": [],
  "provider_url": "https://open.spotify.com/playlist/..."
}
```

### POST /providers/{provider}/playlists

Provider上にプレイリストを作成する。

Headers:

```http
Authorization: Bearer <JWT>
Content-Type: application/json
```

Body:

```json
{
  "title": "Playlist Title",
  "description": "Description",
  "track_ids": ["provider-track-id"]
}
```

Response `200`:

```json
{
  "provider": "spotify",
  "provider_playlist_id": "playlist-id",
  "title": "Playlist Title",
  "tracks": [],
  "provider_url": "https://open.spotify.com/playlist/..."
}
```

### POST /providers/{provider}/playlists/{playlist_id}/tracks

Provider上のプレイリストに曲を追加する。

Headers:

```http
Authorization: Bearer <JWT>
Content-Type: application/json
```

Body:

```json
{
  "track_ids": ["provider-track-id"]
}
```

Response `200`:

```json
{
  "status": "ok"
}
```

## Posts

### GET /posts

タイムライン投稿を取得する。

Headers:

```http
なし
```

Query:

```text
limit=50
before=2026-05-20T00:00:00
```

Response `200`:

```json
{
  "items": [
    {
      "id": "post-id",
      "user_id": "user-id",
      "track_id": "canonical-track-id",
      "source_provider_track_id": "provider-track-row-id",
      "item_type": "track",
      "caption": "Great track",
      "visibility": "public",
      "created_at": "2026-05-20T00:00:00",
      "playback": {
        "provider": "spotify",
        "provider_track_id": "spotify-track-id",
        "title": "Track Title",
        "artist_name": "Artist Name",
        "album_name": "Album Name",
        "duration_ms": 180000,
        "artwork_url": "https://...",
        "provider_url": "https://open.spotify.com/track/...",
        "preview_url": null,
        "playback_id": "spotify-track-id",
        "is_playable": true
      }
    }
  ],
  "next_before": "2026-05-20T00:00:00"
}
```

### POST /posts

曲投稿を作成する。

投稿前に `GET /providers/{provider}/tracks/{track_id}/playback` を呼び、`provider_tracks` を保存しておく必要がある。

Headers:

```http
Authorization: Bearer <JWT>
Content-Type: application/json
```

Body:

```json
{
  "provider": "spotify",
  "provider_track_id": "spotify-track-id",
  "caption": "Great track",
  "visibility": "public"
}
```

Response `201`:

```json
{
  "id": "post-id",
  "user_id": "user-id",
  "track_id": "canonical-track-id",
  "source_provider_track_id": "provider-track-row-id",
  "item_type": "track",
  "caption": "Great track",
  "visibility": "public",
  "created_at": "2026-05-20T00:00:00",
  "playback": {
    "provider": "spotify",
    "provider_track_id": "spotify-track-id",
    "title": "Track Title",
    "artist_name": "Artist Name",
    "album_name": "Album Name",
    "duration_ms": 180000,
    "artwork_url": "https://...",
    "provider_url": "https://open.spotify.com/track/...",
    "preview_url": null,
    "playback_id": "spotify-track-id",
    "is_playable": true
  }
}
```

Error:

- `401`: JWTが無効
- `404`: `provider/provider_track_id` に対応するprovider trackが存在しない
