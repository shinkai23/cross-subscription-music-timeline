# iOS MVP

このフォルダには、SwiftUI iOS MVP の Xcode プロジェクトとアプリ実装を置いています。

現在のMVPは Apple Developer Program 登録なしで確認できる範囲を優先し、MusicKit再生やApple Developer Tokenはまだ扱いません。Spotifyを中心に、Backend API接続、Timeline表示、曲検索、投稿作成、認証、Spotify接続MVPまでを確認できます。

## 実装済みの主な導線

- `GET /posts` によるTimeline表示
- 投稿カードで artwork / title / artist / album / caption / provider を表示
- Spotify `preview_url` がある場合のAVPlayer試聴
- `provider_url` によるSpotify / Apple Music外部遷移
- 曲検索、playback取得、caption付き投稿作成
- ユーザー作成、handleによるdev login、JWT保存・復元、`GET /me` 検証、logout
- Account画面でのSpotify接続MVP
- Provider未接続時のSpotify接続案内UI

## Backend接続

API base URL は `MusicTimelineApp/Support/AppEnvironment.swift` に集約しています。

- Simulator: `http://localhost:4000`
- 実機: `http://192.168.0.12:4000`
- Scheme環境変数 `API_BASE_URL` がある場合はそれを優先

Backendはローカルで以下のように起動します。

```bash
cd backend/api
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

## Build

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineApp \
  -sdk iphonesimulator \
  -quiet build
```

## 現在の制約

- Apple MusicのMusicKit再生は未対応
- Apple Developer Tokenは未使用
- Apple Musicは現時点では外部遷移中心
- Spotify OAuth callbackはMVPとして手動入力方式
- JWTはUserDefaults保存で、Keychain保存は今後対応
- Provider接続状態は一部UserDefaults管理で、本番では接続状態取得APIが必要
