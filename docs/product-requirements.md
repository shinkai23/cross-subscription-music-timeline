# 要件定義

## 目的

Apple Music と Spotify の間にある「共有しにくさ」を減らす。

ユーザーは好きな曲を紹介文付きで投稿し、受け手は自分の利用している音楽サービスで開いたり、タイムライン上で試聴したりできる。

## 課題

音楽配信サービスごとに、同じ楽曲でも異なるIDが割り当てられる。

そのため、Spotify の曲リンクを Apple Music ユーザーが受け取った場合、またはその逆の場合に、同じ曲として扱いづらい。

## MVPスコープ

- ユーザー作成
- handleによる開発用ログイン
- JWT認証、Keychain保存・復元、`/me` 検証、logout
- Spotifyアカウント連携MVP
- Apple Music / Spotify adapter pattern
- 曲検索
- 曲の再生メタデータ取得
- canonical track model
- 曲投稿
- タイムライン取得
- タイムライン上の試聴情報表示
- provider URLによる外部遷移

## MVP達成済み項目

- iOS Timeline表示
- Backend `GET /posts` 取得
- 曲投稿カード表示
- artwork / title / artist / album / caption / provider 表示
- Spotify `preview_url` がある場合のAVPlayer試聴
- `provider_url` によるSpotify / Apple Music外部遷移
- 曲検索
- playback metadata取得
- caption付き投稿作成
- 投稿成功後のTimeline再取得
- ユーザー作成
- handleによる開発用ログイン
- JWT Keychain保存・復元
- `/me` 検証
- logout
- Spotify接続MVP
- Provider接続状態取得API
- SafariでSpotify認可URLを開く
- callback URLまたは `code` / `state` の手動入力
- `POST /auth/spotify/connect`
- Account画面でSpotify接続状態表示

## 現在のMVP方針

Apple Developer Program未登録でも進められるように、初期MVPはSpotify中心で進める。

- Spotifyは検索、OAuth接続、playback metadata取得、`preview_url` がある場合の30秒試聴を優先する。
- Apple Musicは現時点では `provider_url` による外部遷移を基本にする。
- Apple Developer Tokenはまだ使わない。
- MusicKitによるApple Music自動再生はまだ実装しない。
- `playback_mode` は `preview` / `external` を返し、将来MusicKitや別再生方式へ差し替えやすくする。

## ユーザーストーリー

1. ユーザーはアカウントを作成できる。
2. ユーザーはJWTで認証されたAPIを利用できる。
3. ユーザーはSpotifyまたはApple Musicアカウントを連携できる。
4. ユーザーは対応プロバイダーから曲を検索できる。
5. ユーザーは曲の再生メタデータを取得できる。
6. Backendは取得した曲を `tracks` と `provider_tracks` に保存できる。
7. ユーザーは曲に紹介文を付けて投稿できる。
8. ユーザーはタイムラインで投稿一覧を見られる。
9. タイムラインには試聴やprovider遷移に必要なメタデータが含まれる。

## タイムラインカード

MVPのタイムラインカードに表示する情報:

- 投稿者
- 楽曲タイトル
- アーティスト名
- アルバム名
- アートワーク
- 紹介文
- provider URL
- preview URL
- 再生可否

## 投稿フロー

投稿前に、クライアントは対象プロバイダーの楽曲再生情報を取得する。

```text
GET /providers/{provider}/tracks/{track_id}/playback
```

Backendはprovider APIから取得した情報をもとに、楽曲を保存する。

```text
tracks
  楽曲そのもの

provider_tracks
  Spotify / Apple Music 上の楽曲情報
```

その後、クライアントは投稿を作成する。

```text
POST /posts
```

```json
{
  "provider": "spotify",
  "provider_track_id": "spotify-track-1",
  "caption": "Great track"
}
```

Backendは `provider/provider_track_id` から `provider_tracks` を解決し、投稿には以下を保存する。

```text
posts.track_id
posts.source_provider_track_id
```

## 楽曲マッチング方針

MVPでは以下の優先順位で canonical track に紐付ける。

1. `(provider, provider_track_id)` で既存の `ProviderTrack` を探す。
2. ISRCで既存の `Track` を探す。
3. 見つからなければ新しい `Track` を作成する。

ISRCがない曲でも、同じプロバイダー上の同じ曲を再取得しただけで `tracks` が重複作成されないように、`ProviderTrack` を先に確認する。

## 対象外

MVPでは以下を対象外とする。

- 本番パスワード認証
- OAuthログインによるアプリ認証
- ASWebAuthenticationSessionによるSpotify callback自動処理
  - 導入時はSpotify Developer Dashboard、Backend `SPOTIFY_REDIRECT_URI`、iOS URL schemeを `musictimeline://auth/spotify/callback` などに揃える。
- Apple Music MusicKit再生
- Apple Developer Tokenを使うApple Music API運用
- Apple Musicアカウント連携UI
- フォロー中ユーザーのタイムライン
- アルバム投稿
- プレイリスト投稿
- プレイリスト再現
- 曖昧なマッチング候補のユーザー確認
- いいね
- コメント
- 保存
- 通報・管理者モデレーション
- AI補助タグ
- ユーザーのメインサービスに応じたprovider fallback

## 制約

- 音源ファイルを生成、保存、アップロード、再配布しない。
- SpotifyやApple Musicをスクレイピングしない。
- Spotifyの30秒preview URLだけに依存した再生設計にしない。
- 歌詞全文を投稿・保存しない。
- Spotify ContentやApple Music由来のコンテンツをAIモデル学習に使わない。
- Provider tokenは暗号化して保存する。
- 各Providerが求める表示ルール、リンクバック、権限scopeを守る。

## 成功指標

- Provider連携完了率
- 曲投稿作成数
- タイムライン取得数
- タイムライン上で試聴可能な投稿の割合
- 投稿を開いてから再生またはprovider遷移に至るまでの時間
