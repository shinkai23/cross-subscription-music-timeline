# MVP提出前チェックリスト

このチェックリストは、現在のiOS MVPをポートフォリオ提出またはデモ前に確認するためのものです。

## 対象範囲

- iOS Timeline表示
- Spotify中心の曲検索、試聴、投稿作成
- handleによる開発用ログイン
- Spotify provider接続MVP
- Apple Developer Program登録なしで確認できる範囲

## 実装確認

- [ ] 未認証時にAuth画面が表示される。
- [ ] `display_name` / `handle` / `primary_provider` でユーザーを作成できる。
- [ ] handle dev loginでJWTを取得できる。
- [ ] Keychainに保存済みのJWTをアプリ起動時に復元し、`GET /me` で検証できる。
- [ ] logoutでJWTとローカル接続状態がクリアされる。
- [ ] Timelineで `GET /posts` の投稿一覧が表示される。
- [ ] 投稿カードにartwork、曲名、artist、album、caption、providerが表示される。
- [ ] `preview_url` があるSpotify投稿だけ試聴ボタンが有効になる。
- [ ] `provider_url` からSpotifyまたはApple Musicを外部で開ける。
- [ ] Account画面でSpotify接続状態が表示される。
- [ ] Spotify未接続時、曲検索または投稿作成で接続案内が表示される。
- [ ] Spotify接続導線から認可URLをSafariで開ける。
- [ ] callback URL、または `code` / `state` の手動入力で `POST /auth/spotify/connect` できる。
- [ ] Spotify接続後、曲検索結果が表示される。
- [ ] 検索結果から曲を選び、caption付きで投稿できる。
- [ ] 投稿成功後にTimelineへ戻り、一覧が再取得される。
- [ ] Apple Music選択時は、現在のMVPでは連携未対応であることがUIに表示される。

## API確認

- [ ] `POST /auth/dev-login` は既存ユーザーhandleでJWTを返す。
- [ ] dev loginで返ったJWTを使って `GET /me` が成功する。
- [ ] 存在しないhandleでは `POST /auth/dev-login` が404を返す。
- [ ] `GET /posts` の `playback` に `playback_mode` が含まれる。
- [ ] Spotifyの `preview_url` がある場合は `playback_mode = "preview"` になる。
- [ ] Spotifyの `preview_url` がない場合は `playback_mode = "external"` になる。
- [ ] Apple Musicは `playback_mode = "external"` になる。
- [ ] `POST /posts` のレスポンスにも最新の `playback` 情報が含まれる。

## デモ確認

1. Backendを起動する。
2. iOS Simulatorでアプリを起動する。
3. Auth画面でユーザーを作成する。
4. handle dev loginで認証済み状態にする。
5. Account画面でSpotify接続を開始する。
6. SafariでSpotify認可URLを開く。
7. callback URL、または `code` / `state` を手動入力する。
8. Account画面で `Spotify connected` を確認する。
9. 曲検索画面でSpotify曲を検索する。
10. 曲を選択してcaption付きで投稿する。
11. Timelineに投稿が表示されることを確認する。
12. 試聴可能な曲ではpreview再生を確認する。
13. Providerで開くボタンからSpotifyを開く。

## スクリーンショット

README用の画像は `docs/images/` に配置する。

- [ ] `docs/images/auth.png`
- [ ] `docs/images/timeline.png`
- [ ] `docs/images/spotify-connect.png`
- [ ] `docs/images/track-search.png`
- [ ] `docs/images/create-post.png`
- [ ] `docs/images/provider-required.png`

## 検証コマンド

Backend:

```bash
cd backend/api
ruff check .
pytest
```

iOS app target:

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineApp \
  -sdk iphonesimulator \
  -quiet build
```

iOS test targets:

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineAppTests \
  -configuration Debug \
  -sdk iphonesimulator \
  -quiet build

DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineAppUITests \
  -configuration Debug \
  -sdk iphonesimulator \
  -quiet build
```

Repository hygiene:

```bash
git diff --check
```

## 既知の制約

- `/auth/dev-login` はMVP/開発用であり、本番では無効化または保護が必要。
- 本格的なパスワード認証、OAuthログイン、token refreshは未対応。
- JWTはKeychain保存。既存UserDefaults tokenは起動時にKeychainへ移行して削除する。
- Spotify OAuth callbackは手動入力方式。
- `ASWebAuthenticationSession` とカスタムURLスキーム callback は未対応。
- Provider接続状態は一部UserDefaults管理であり、本番ではprovider接続状態取得APIが必要。
- Apple MusicのMusicKit再生は未対応。
- Apple Developer Tokenは未使用。
- Apple Musicは現時点では外部遷移中心。
- Spotify / Apple Musicの音源ファイルは保存・再配布しない。
