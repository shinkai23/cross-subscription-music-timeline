# ドメインモデル設計

このドキュメントでは、Cross-Subscription Music Timeline のバックエンドにおける主要なドメインモデル設計を説明する。

本アプリケーションでは、Spotify / Apple Music など異なる音楽サブスクリプションサービス上に存在する同一楽曲を、アプリケーション内では同じ楽曲として扱うことを目的としている。

そのため、楽曲そのものを表す情報と、各プロバイダー固有の再生情報を分離して管理する。

## 解決したい課題

音楽配信サービスごとに、同じ楽曲であっても異なるIDが割り当てられる。

例:

```text
Spotify:
  provider = spotify
  provider_track_id = spotify_track_123

Apple Music:
  provider = apple_music
  provider_track_id = apple_music_track_456
```

これらが同じ楽曲を指していても、プロバイダーIDだけで管理すると別々の曲として扱われてしまう。

本アプリケーションでは、以下のように分離する。

```text
tracks
  楽曲そのもの

provider_tracks
  Spotify / Apple Music 上の楽曲情報

posts
  タイムライン投稿
```

この構造により、Spotifyユーザーが投稿した曲であっても、Apple Musicユーザーは同じ canonical track を起点に、自分の利用サービスに合った再生情報を取得できる。

## ER図について

このドキュメントでは、draw.ioで作成したER図をPNG画像として掲載する。

ER図は2つに分けている。

- コアドメインER図: クロスサブスクリプション投稿機能の中核となるテーブル関係
- 周辺機能ER図: 通報、プレイリスト、マッチング基盤などの補助機能

## テーブル間の関係一覧

| 親テーブル | 関係 | 子テーブル | 意味 |
|---|---:|---|---|
| users | 1 -> N | service_accounts | 1人のユーザーは複数の外部サービス連携を持てる |
| users | 1 -> N | posts | 1人のユーザーは複数の投稿を作成できる |
| users | 1 -> N | reports | 1人のユーザーは複数の通報を作成できる |
| tracks | 1 -> N | provider_tracks | 1つの楽曲は複数サービス上の楽曲情報を持てる |
| tracks | 1 -> N | posts | 1つの楽曲は複数投稿から参照される |
| provider_tracks | 1 -> N | posts | 1つのprovider trackは複数投稿の投稿元になれる |
| posts | 1 -> N | reports | 1つの投稿は複数回通報される可能性がある |
| playlists | 1 -> N | playlist_items | 1つのプレイリストは複数の曲を含む |
| tracks | 1 -> N | playlist_items | 1つの楽曲は複数プレイリスト項目から参照される |

## コアドメインER図

![コアドメインER図](./ER-diagram1.png)

この図は、アプリケーションの中核であるクロスサブスクリプション投稿機能を表す。

主な関係は以下である。

| 親テーブル | 関係 | 子テーブル | 意味 |
|---|---:|---|---|
| users | 1 -> N | service_accounts | 1人のユーザーは複数サービスと連携できる |
| users | 1 -> N | posts | 1人のユーザーは複数の投稿を作成できる |
| tracks | 1 -> N | provider_tracks | 1つの楽曲は複数サービス上の楽曲情報を持てる |
| tracks | 1 -> N | posts | 1つの楽曲は複数投稿から参照される |
| provider_tracks | 1 -> N | posts | 1つのprovider trackは投稿元として使われる |

## コアドメインの説明

### Track

`tracks` は楽曲そのものを表す canonical entity である。

特定のプロバイダーには依存せず、Spotify / Apple Music / 将来追加されるプロバイダーを横断して共有できる楽曲情報を保持する。

主な責務は以下である。

- サービス横断で同一楽曲を表す
- 投稿やマッチング処理で利用する安定した楽曲IDを提供する
- タイトル、アーティスト、アルバム、再生時間、アートワーク、ISRCなどの共通メタデータを保持する

主なカラム:

- `id`
- `isrc`
- `title`
- `artist_name`
- `album_name`
- `duration_ms`
- `artwork_url`
- `canonical_source`

### ProviderTrack

`provider_tracks` は、各音楽プロバイダー上に存在する楽曲情報を表す。

1つの `Track` に対して、Spotify版、Apple Music版など複数の `ProviderTrack` が紐づく。

主な責務は以下である。

- プロバイダー固有の楽曲IDを保持する
- タイムライン再生に必要なURLやIDを保持する
- preview URL、provider URL、playback IDなどを保持する
- `(provider, provider_track_id)` によって同一プロバイダー上の重複を防ぐ
- プロバイダー固有の追加情報を `provider_metadata` に保持する

主なカラム:

- `id`
- `track_id`
- `provider`
- `provider_track_id`
- `playback_id`
- `preview_url`
- `provider_url`
- `is_playable`
- `playback_source`
- `provider_metadata`

### Post

`posts` はタイムライン上の投稿を表す。

投稿は canonical な `Track` を参照しつつ、投稿元として利用された `ProviderTrack` も保持する。

主な責務は以下である。

- タイムライン投稿を保持する
- 投稿対象の楽曲を canonical track として参照する
- 投稿時に利用されたプロバイダー上の楽曲情報を保持する
- タイムライン取得時に再生情報を付与できるようにする

主なカラム:

- `id`
- `user_id`
- `track_id`
- `source_provider_track_id`
- `item_type`
- `caption`
- `visibility`
- `created_at`

## 具体例

ある曲 `Song A` がSpotifyとApple Musicの両方に存在するとする。

```text
tracks
- track_1: Song A

provider_tracks
- provider_track_1: track_1 / spotify / spotify_song_a
- provider_track_2: track_1 / apple_music / apple_song_a

posts
- post_1: track_1 / provider_track_1
```

この場合、`post_1` はSpotify上の楽曲を元に投稿されている。

しかし、投稿対象の楽曲そのものは `track_1` である。

そのため、Apple Musicユーザーが同じ投稿を見る場合でも、`track_1` を起点にApple Music側の `provider_track_2` を探すことで、自分の利用サービスに合った再生情報を利用できる。

## Track と ProviderTrack を分離する理由

本アプリケーションでは、異なる音楽サブスクリプション間で同じ楽曲を扱う必要がある。

もし楽曲をプロバイダー単位でのみ保存すると、同じ楽曲であっても以下のように別物として扱われる。

```text
spotify:track:123
apple_music:track:456
```

この場合、タイムライン上では同じ曲であっても別々の投稿対象として扱われる。

そこで、楽曲そのものを `tracks` に保存し、SpotifyやApple Music上の個別情報を `provider_tracks` に分離する。

この設計により、以下が可能になる。

- 同一楽曲をプロバイダー横断でまとめられる
- プロバイダー固有の再生情報を分離できる
- 将来プロバイダーを追加しても `tracks` の構造を大きく変えずに済む
- 投稿は安定した canonical track を参照できる

## ProviderTrack をプロバイダーごとに分けない理由

現時点では、`spotify_provider_tracks` や `apple_music_provider_tracks` のようにテーブルを分けず、単一の `provider_tracks` テーブルで管理する。

理由は、タイムライン再生に必要な主要フィールドがプロバイダー間で共通しているためである。

共通する情報の例:

- プロバイダー上の楽曲ID
- preview URL
- provider URL
- playback ID
- artwork URL
- 再生可否
- raw metadata

プロバイダーごとの差分は `provider_metadata` にJSONとして保持する。

将来的に特定プロバイダーだけが持つ情報がアプリケーション上で重要になった場合は、以下のような詳細テーブルを追加する余地を残している。

```text
tracks
provider_tracks
spotify_track_details
apple_music_track_details
```

## 楽曲マッチング方針

プロバイダーから再生情報を取得した際、バックエンドは以下の優先順位で canonical `Track` との紐付けを行う。

1. `(provider, provider_track_id)` で既存の `ProviderTrack` を探す
2. ISRCで既存の `Track` を探す
3. 見つからなければ新しい `Track` を作成する

この順序により、ISRCが存在しない楽曲であっても、同じプロバイダー上の同じ楽曲を再取得しただけで `tracks` が重複作成されることを防ぐ。

将来的な改善候補:

- title + main artist + album
- title + main artist + duration proximity
- normalized version title
- uncertain match のユーザーレビュー

## 投稿フロー

クライアントは投稿作成時に `track_id` を直接送らない。

代わりに、プロバイダー上の楽曲IDを送信する。

```json
{
  "provider": "spotify",
  "provider_track_id": "spotify-track-1",
  "caption": "Great track"
}
```

バックエンドはこの情報から `provider_tracks` を解決し、投稿には以下を保存する。

```text
provider/provider_track_id
↓
provider_tracks.id
↓
provider_tracks.track_id
↓
posts.track_id
posts.source_provider_track_id
```

この設計により、クライアントAPIは扱いやすく、DBは正規化された状態を保てる。

## タイムライン再生

タイムライン取得時には、`posts` から `source_provider_track_id` をたどり、`provider_tracks` の再生情報をレスポンスに含める。

これにより、iOSアプリはタイムライン上で以下の情報を利用できる。

- title
- artist name
- album name
- artwork URL
- preview URL
- provider URL
- playback ID
- is playable

MVPでは `preview_url` を用いた試聴再生を優先する。

将来的には、ユーザーの接続済みプロバイダーやMusicKit / Spotify SDKの状態に応じて、`playback_id` を使ったフル再生やプロバイダーアプリへの遷移を行う。

## 周辺機能ER図

![周辺機能ER図](./ER-diagram2.png)

この図は、通報、プレイリスト、マッチング基盤などの周辺機能を表す。

主な関係は以下である。

| 親テーブル | 関係 | 子テーブル | 意味 |
|---|---:|---|---|
| users | 1 -> N | reports | 1人のユーザーは複数の通報を作成できる |
| posts | 1 -> N | reports | 1つの投稿は複数回通報される可能性がある |
| users | 1 -> N | playlists | 1人のユーザーは複数のプレイリストを持てる |
| playlists | 1 -> N | playlist_items | 1つのプレイリストは複数項目を持つ |
| tracks | 1 -> N | playlist_items | 1つの楽曲は複数プレイリスト項目から参照される |
| tracks | 1 -> N | track_matches | 1つの楽曲は複数のマッチ候補に関わる |

## 周辺機能の説明

### Report

`reports` は投稿に対する通報を表す。

ユーザーは不適切な投稿を通報でき、運営側は `status` によって対応状況を管理できる。

### Playlist

`playlists` は外部プロバイダー上のプレイリストを表す。

SpotifyやApple Music上に作成されたプレイリスト情報を保持する。

### PlaylistItem

`playlist_items` はプレイリスト内の楽曲を表す。

1つのプレイリストは複数の `playlist_items` を持ち、各項目は canonical `Track` を参照する。

### TrackMatch

`track_matches` は、プロバイダー間の楽曲マッチング候補を表す。

現時点では初期設計の名残として、`source_provider` / `source_track_id` / `target_provider` / `target_track_id` を保持している。

今後、`provider_tracks.id` または canonical `tracks.id` を使った設計へ移行する余地がある。

## 今後の改善点

今後の改善候補は以下である。

- `track_matches` の canonical track ベースへの整理
- provider fallback の設計
- ユーザーが接続しているプロバイダーに応じた再生情報の選択
- Spotify / Apple Music SDK連携時の再生可否判定
- `provider_metadata` に保存するJSON構造の明文化
- API仕様書への投稿フロー反映
