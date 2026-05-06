# アーキテクチャ

## 全体像

```text
iOS App
  SwiftUI
  MusicKit
  サービス認可 UI
  タイムライン
  プレイリスト変換レビュー

Android App
  Jetpack Compose
  サービス認可 UI
  タイムライン
  プレイリスト変換レビュー

Backend API
  認証 / セッション
  投稿
  タイムライン
  楽曲メタデータ
  プレイリスト変換
  モデレーション

Workers
  メタデータ更新
  サービス間マッチング
  変換結果分析

Database
  PostgreSQL
```

## Backend モジュール

- `auth`: アプリのセッションと Provider アカウント連携
- `providers`: Apple Music / Spotify アダプター
- `catalog`: 正規化した曲、アルバム、アーティスト、プレイリストのメタデータ
- `posts`: 投稿とタイムライン取得
- `matching`: サービス間の楽曲マッチング
- `conversion`: 変換先サービスでのプレイリスト作成
- `moderation`: 通報、削除、ブロック
- `ai`: テキスト限定の紹介文・タグ補助

## Provider Adapter

Provider ごとの差を Backend 内に閉じ込めるため、Apple Music と Spotify は共通インターフェースで扱います。

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

## マッチング戦略

優先順位:

1. ISRC 完全一致
2. 曲名 + メインアーティスト + アルバム
3. 曲名 + メインアーティスト + 再生時間の近さ
4. バージョン表記を正規化した曲名
5. ユーザーが候補から選択

マッチング結果には、信頼度と理由を保存します。

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

## データモデル案

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

## iOS 優先方針

Apple Music を重視するため、最初は SwiftUI と MusicKit を中心に作ります。

初期画面:

- サービス選択
- Apple Music 認可
- タイムライン
- 投稿作成
- プレイリスト変換レビュー
- プロフィール
- 通報シート

## セキュリティ

- Provider token は Backend で暗号化保存する。
- Spotify のモバイル認可は PKCE を使う。
- Apple Music の秘密鍵はサーバー側だけで扱う。
- アプリセッションは短めにする。
- Provider 権限 scope は最小限にする。
- アカウント連携解除とデータ削除導線を用意する。

