# iOS MVPデモ手順

この手順は、Apple Developer Program登録なしで確認できる現在のMVPを対象にする。

## 事前条件

- Backendが `http://localhost:4000` で起動している。
- iOS Simulatorでアプリを起動する。
- Spotify OAuthを試す場合は、Backendの `SPOTIFY_CLIENT_ID` と `SPOTIFY_REDIRECT_URI` が設定され、Spotify Developer Dashboard側にも同じredirect URIが登録されている。

## Backend起動

```bash
cd backend/api
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

## iOSビルド

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineApp \
  -sdk iphonesimulator \
  -quiet build
```

## デモフロー

1. iOSアプリを起動する。
2. 未認証画面でユーザーを作成する。作成後、同じhandleでdev loginを自動実行する。
3. 自動ログインできない場合は、handleでdev loginする。
4. Account画面を開く。
5. `Connect Spotify` を押す。
6. Spotify認可URLをSafariで開く。
7. 認可後のcallback URL、または `code` / `state` をアプリに手動入力する。
8. `Connect Spotify` を押してBackendへ `POST /auth/spotify/connect` する。
9. Account画面で `Spotify connected` を確認する。
10. 下部Composeボタン、またはTimelineの `+` から曲検索を開く。
11. Spotifyで曲を検索する。
12. 曲を選択し、captionを入力して投稿する。
13. 投稿成功後、Timelineに投稿が表示される。
14. `preview_url` がある投稿はAVPlayerで試聴する。
15. `provider_url` からSpotifyを開く。

## スクリーンショット撮影手順

README掲載用の画像は `docs/images/` に配置する。現在はREADMEが崩れないように同名のプレースホルダーPNGを置いている。撮影後、同じファイル名で差し替える。

撮影時の推奨:

- iOS Simulatorの端末サイズを統一する。
- ステータスバーや時刻の見え方が画面ごとに大きく変わらないようにする。
- Demo用のhandle、caption、検索キーワードは見られても問題ない内容にする。
- Spotify未接続状態と接続済み状態を分けて撮影する。
- 実画像に差し替えたあと、README上で画像が横並びでも読みやすいか確認する。

| ファイル | 撮影対象 | 確認したい内容 |
| --- | --- | --- |
| `docs/images/auth.png` | Auth / Handle login | ユーザー作成、handleログイン、JWT認証の入口 |
| `docs/images/timeline.png` | Timeline | 投稿カード、caption、provider、preview、外部遷移 |
| `docs/images/spotify-connect.png` | Spotify connection | Account画面のSpotify接続状態と接続導線 |
| `docs/images/track-search.png` | Track search | provider選択、検索入力、検索結果一覧 |
| `docs/images/create-post.png` | Create post | 曲情報表示、caption入力、投稿ボタン |
| `docs/images/provider-required.png` | Provider connection required | Spotify未接続時の接続案内 |

## 制約

- `/auth/dev-login` は開発用。
- Spotify callbackは手動入力方式。
- ASWebAuthenticationSessionは未対応。
- JWTはUserDefaults保存。
- Provider接続状態は一部UserDefaults管理。
- Apple Musicは外部遷移中心。
- MusicKit再生とApple Developer Tokenは未対応。
