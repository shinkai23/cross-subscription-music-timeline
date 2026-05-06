# GitHub バックログ

リモートリポジトリ作成後、以下を GitHub Issues として登録します。

## Milestone: Foundation

### 1. MVP 向け Provider 規約を確認する

Labels: `legal-risk`, `research`

受け入れ条件:

- Apple Music API と MusicKit の規約を確認する。
- Spotify Developer Policy と Web API の制限を確認する。
- README と法務リスク文書を最新リンクと判断内容で更新する。

### 2. Xcode プロジェクトを作成し SwiftUI 骨格を取り込む

Labels: `feature`, `ios`

受け入れ条件:

- 最新安定版 Xcode でプロジェクトがビルドできる。
- `apps/ios/MusicTimelineApp` 以下のファイルが取り込まれている。
- アプリ起動時にタイムラインタブが表示される。

### 3. Apple Music capability と認可処理を追加する

Labels: `feature`, `ios`, `apple-music`

受け入れ条件:

- アプリが MusicKit 認可を要求できる。
- authorized、denied、restricted の状態を表示できる。
- Apple Music サブスクリプション状態を確認できる。

### 4. Apple Music カタログ検索を実装する

Labels: `feature`, `ios`, `apple-music`

受け入れ条件:

- ユーザーが曲とアルバムを検索できる。
- 結果にタイトル、アーティスト、アートワーク、Provider リンクを表示できる。
- 選択した結果を投稿下書きに使える。

### 5. Backend API をローカル起動する

Labels: `feature`, `backend`

受け入れ条件:

- `GET /health` が成功する。
- `GET /posts` がモックタイムラインを返す。
- CI で TypeScript 型チェックが通る。

## Milestone: Playlist Conversion MVP

### 6. Spotify OAuth PKCE を実装する

Labels: `feature`, `spotify`, `backend`

受け入れ条件:

- ユーザーが PKCE で Spotify 連携できる。
- 許可された scope を保存できる。
- 連携解除時に Provider アカウントデータを削除できる。

### 7. Spotify プレイリストを取り込む

Labels: `feature`, `spotify`, `backend`

受け入れ条件:

- ユーザーが Spotify プレイリストを貼り付けまたは選択できる。
- Backend が正規化したプレイリストメタデータを保存できる。
- ローカルファイルや利用不可曲を明確に表示できる。

### 8. ISRC マッチングを実装する

Labels: `feature`, `matching`

受け入れ条件:

- ISRC 完全一致を高信頼度として扱う。
- ISRC がない場合だけ曲名・アーティスト fallback を使う。
- マッチ理由と信頼度を保存する。

### 9. プレイリスト変換レビュー UI を作る

Labels: `feature`, `ios`, `matching`

受け入れ条件:

- 一致、要確認、未対応の曲が見分けられる。
- ユーザーが未対応曲や誤一致を除外できる。
- プレイリスト作成前にユーザー確認を必須にする。

### 10. マッチ済み曲から Apple Music プレイリストを作成する

Labels: `feature`, `ios`, `apple-music`

受け入れ条件:

- 確認済みの曲を Apple Music ライブラリ内の新規プレイリストに書き込める。
- 失敗時に対処しやすいメッセージを表示する。
- 変換結果を記録する。

## Milestone: Safety

### 11. 通報とモデレーションのデータフローを追加する

Labels: `feature`, `moderation`

受け入れ条件:

- ユーザーが投稿を通報できる。
- 通報理由と詳細を保存できる。
- 著作権通報の理由を選べる。

### 12. AI テキスト補助のガードレールを追加する

Labels: `feature`, `ai`, `legal-risk`

受け入れ条件:

- AI は紹介文、タグ、要約だけを生成する。
- 音声生成と歌詞全文生成の要求を拒否する。
- AI が参照した入力の種類を監査用に記録する。

