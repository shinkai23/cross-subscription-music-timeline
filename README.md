# Cross-Subscription Music Timeline

Apple Music と Spotify の間にある「共有しにくさ」を減らすための、iOS 重視の音楽投稿・プレイリスト再現アプリです。

ユーザーは好きな曲、アルバム、自作プレイリストを紹介文付きで投稿できます。タイムラインでは投稿された音楽が並び、受け手は自分が選んだサブスクリプション、たとえば Apple Music または Spotify で開いたり、可能な範囲でプレイリストを再現したりできます。

このリポジトリは学習用ポートフォリオとして、プロダクト設計、iOS 実装、バックエンド設計、GitHub 運用、著作権・外部 API リスクへの配慮をまとめて見せることを目的にしています。

## プロダクトの核

このアプリの価値は、単なる音楽 SNS ではなく、**サービスをまたいだプレイリスト共有・再現**にあります。

例:

- Spotify ユーザーが自作プレイリストを投稿する。
- Apple Music ユーザーがその投稿を見る。
- アプリが ISRC や曲名・アーティスト名を使って Apple Music 上の同じ曲を探す。
- ユーザーが確認したうえで Apple Music にプレイリストを作成する。

## MVP で実現すること

1. 曲、アルバム、プレイリストを紹介文付きで投稿する。
2. 投稿をタイムライン形式で表示する。
3. ユーザーがメインの音楽サービスを選択する。
4. Apple Music / Spotify の公式リンクへ遷移できる。
5. ISRC を優先して楽曲をサービス間でマッチングする。
6. プレイリスト変換前に一致・要確認・未対応の曲を表示する。
7. AI は紹介文、タグ、要約などのテキスト補助だけに使う。
8. 通報、削除、著作権リスク対応を最初から設計に含める。

## やらないこと

著作権と各サービスの規約を守るため、以下は明確に対象外です。

- 音源ファイルを生成、保存、アップロード、再配布しない。
- Spotify や Apple Music をスクレイピングしない。
- Spotify の 30 秒 preview URL に依存しない。
- 歌詞全文を投稿・保存しない。
- Spotify Content や Apple Music 由来のコンテンツを AI モデル学習に使わない。
- Apple、Apple Music、Spotify、アーティスト、レーベルから公認されたように見せない。

## 技術構成

- iOS: SwiftUI, MusicKit, Apple Music API
- Android: Kotlin, Jetpack Compose を想定。iOS MVP 後に着手
- Backend: TypeScript, Fastify, PostgreSQL, Prisma
- Matching: ISRC 優先、曲名・アーティスト・アルバム・再生時間で補助
- CI: GitHub Actions
- 開発管理: GitHub Issues, Pull Requests, Projects を想定

## ローカル開発

バックエンドは Node.js 22、npm、Docker が必要です。

```bash
docker compose up -d postgres
cd backend/api
cp .env.example .env
npm install
npm run typecheck
npm test
npm run dev
```

API は標準で `http://127.0.0.1:4000` を使います。

iOS はこの Windows 環境では Xcode プロジェクトを生成・ビルドできないため、`apps/ios/MusicTimelineApp` 以下の Swift ファイルを macOS 上の Xcode プロジェクトへ取り込む前提です。

## ドキュメント

- [要件定義](docs/product-requirements.md)
- [法務・外部 API リスク](docs/legal-and-platform-risk.md)
- [アーキテクチャ](docs/architecture.md)
- [ロードマップ](docs/roadmap.md)
- [GitHub セットアップ](docs/github-setup.md)
- [ローカル開発手順](docs/local-development.md)
- [Provider 連携設計](docs/provider-integration.md)
- [ADR 0001: 音楽音源を生成・保存しない](docs/adr/0001-no-generated-audio.md)

## ファイル構成と解説

### ルート

| ファイル | 役割 |
| --- | --- |
| `README.md` | このファイル。プロダクト概要、開発方針、全ファイルの説明を日本語でまとめる。 |
| `LICENSE` | GitHub 作成時に追加したライセンスファイル。 |
| `.gitignore` | OS、エディタ、Xcode、Android、Node.js、環境変数、ログなどの不要ファイルを Git 管理から除外する。 |
| `CONTRIBUTING.md` | ブランチ運用、PR 方針、コミット方針、安全ルールをまとめる。 |
| `docker-compose.yml` | ローカル開発用 PostgreSQL を起動する Docker Compose 設定。 |

### GitHub 設定

| ファイル | 役割 |
| --- | --- |
| `.github/ISSUE_TEMPLATE/config.yml` | GitHub Issue 作成画面の設定。外部ポリシー確認用リンクも置く。 |
| `.github/ISSUE_TEMPLATE/feature_request.md` | 機能追加 Issue のテンプレート。目的、範囲、受け入れ条件、法務影響を書かせる。 |
| `.github/ISSUE_TEMPLATE/legal_risk.md` | 著作権、Provider 規約、プライバシーなどのリスク管理用 Issue テンプレート。 |
| `.github/pull_request_template.md` | PR テンプレート。変更概要、テスト、Provider / 法務チェックを含める。 |
| `.github/workflows/backend.yml` | Backend の GitHub Actions。Node.js 22 で依存インストール、型チェック、テストを実行する。 |
| `.github/workflows/docs.yml` | ドキュメント・安全チェック用 GitHub Actions。音声ファイル混入を検出して失敗させる。 |

### iOS アプリ

| ファイル | 役割 |
| --- | --- |
| `apps/ios/README.md` | iOS プロトタイプの取り込み手順。Xcode プロジェクト作成時の注意を書く。 |
| `apps/ios/MusicTimelineApp/MusicTimelineApp.swift` | SwiftUI アプリのエントリーポイント。最初に `RootView` を表示する。 |
| `apps/ios/MusicTimelineApp/Models/MusicModels.swift` | 音楽 Provider、投稿種別、ユーザー、投稿、マッチング概要、変換レビュー項目などの基本モデル。 |
| `apps/ios/MusicTimelineApp/Models/MusicSearchResult.swift` | Apple Music 検索結果を UI で扱うためのモデル。 |
| `apps/ios/MusicTimelineApp/Services/AppleMusicAuthorizationService.swift` | MusicKit の認可状態と Apple Music サブスクリプション状態を取得するサービス。 |
| `apps/ios/MusicTimelineApp/Services/AppleMusicCatalogService.swift` | MusicKit のカタログ検索を使い、曲・アルバム検索結果を `MusicSearchResult` に変換する。 |
| `apps/ios/MusicTimelineApp/Services/MockTimelineService.swift` | iOS UI の表示確認に使うモック投稿とプレイリスト変換データ。 |
| `apps/ios/MusicTimelineApp/Views/RootView.swift` | タブ構成のルート画面。タイムライン、サービス選択、投稿作成を切り替える。 |
| `apps/ios/MusicTimelineApp/Views/ServiceSelectionView.swift` | Apple Music / Spotify のメインサービス選択と Apple Music 認可ボタンを表示する。 |
| `apps/ios/MusicTimelineApp/Views/TimelineView.swift` | 投稿タイムライン、投稿カード、投稿詳細、公式 Provider URL を開く処理を持つ。 |
| `apps/ios/MusicTimelineApp/Views/PostComposerView.swift` | 投稿作成画面。Apple Music 検索、検索結果選択、紹介文入力、AI 下書きボタンの土台。 |
| `apps/ios/MusicTimelineApp/Views/MusicSearchResultRow.swift` | 検索結果の 1 行表示。ジャケット、タイトル、アーティスト、Provider を表示する。 |
| `apps/ios/MusicTimelineApp/Views/PlaylistConversionReviewView.swift` | プレイリスト変換前の確認画面。一致、要確認、未対応の曲を表示する。 |
| `apps/ios/MusicTimelineApp/Views/ReportSheetView.swift` | 投稿通報用のシート。著作権、誤情報、スパム、迷惑行為などの理由を選べる。 |

### Backend API

| ファイル | 役割 |
| --- | --- |
| `backend/api/README.md` | Backend の起動方法、エンドポイント、安全制約をまとめる。 |
| `backend/api/.env.example` | ローカル環境変数のサンプル。DB、Apple Music、Spotify の設定値を定義する。 |
| `backend/api/package.json` | Backend の npm 依存関係と `dev`、`typecheck`、`test` などのスクリプト。 |
| `backend/api/tsconfig.json` | TypeScript コンパイラ設定。ES2022、NodeNext、strict を有効にする。 |
| `backend/api/prisma/schema.prisma` | PostgreSQL 用 Prisma スキーマ。User、ServiceAccount、Post、Track、TrackMatch、Report を定義する。 |
| `backend/api/src/server.ts` | Fastify サーバーの起動処理。CORS、health、auth、posts ルートを登録する。 |
| `backend/api/src/domain/music.ts` | Provider、曲、プレイリスト、マッチング結果など Backend ドメイン型を定義する。 |
| `backend/api/src/routes/health.ts` | `GET /health` の実装。API が起動しているか確認する。 |
| `backend/api/src/routes/auth.ts` | Provider 一覧、Provider 接続、Spotify 認可 URL 生成の API ルート。 |
| `backend/api/src/routes/posts.ts` | `GET /posts` と `POST /posts` の API ルート。現状はモック中心。 |
| `backend/api/src/services/mockPosts.ts` | Backend のモックタイムラインデータ。 |
| `backend/api/src/providers/MusicProviderAdapter.ts` | Apple Music / Spotify など Provider 実装が満たすべき共通インターフェース。 |
| `backend/api/src/providers/appleMusicAdapter.ts` | Apple Music Provider のアダプター雛形。検索、取得、作成は未実装として境界だけ定義。 |
| `backend/api/src/providers/spotifyAdapter.ts` | Spotify Provider のアダプター雛形。検索、取得、作成は未実装として境界だけ定義。 |
| `backend/api/src/providers/spotifyAuth.ts` | Spotify OAuth PKCE の authorize URL を生成する処理と初期 scope 定義。 |
| `backend/api/src/matching/trackMatcher.ts` | ISRC、曲名、アーティスト、アルバム、再生時間を使って曲をマッチングする関数。 |
| `backend/api/src/matching/trackMatcher.test.ts` | `trackMatcher.ts` の単体テスト。ISRC 優先、フォールバック、未一致を検証する。 |

### 設計ドキュメント

| ファイル | 役割 |
| --- | --- |
| `docs/product-requirements.md` | プロダクトの課題、目標、対象ユーザー、MVP ユーザーストーリー、成功指標を整理する。 |
| `docs/legal-and-platform-risk.md` | 著作権、歌詞、ジャケット、Spotify / Apple Music 規約、AI 利用、プライバシーのリスクを整理する。 |
| `docs/architecture.md` | iOS、Android、Backend、Worker、DB、Provider Adapter、データモデルの全体設計。 |
| `docs/roadmap.md` | Phase 0 から Phase 7 までの実装ロードマップと進捗チェックリスト。 |
| `docs/provider-integration.md` | Apple Music と Spotify の認可、検索、プレイリスト作成、再生方針を整理する。 |
| `docs/local-development.md` | ローカルで Backend、PostgreSQL、iOS プロトタイプを扱う手順。 |
| `docs/github-setup.md` | GitHub リポジトリ設定、推奨ラベル、初回 push 手順をまとめる。 |
| `docs/github-backlog.md` | GitHub Issue に起こす予定のバックログ。Foundation、Playlist Conversion、Safety に分類。 |
| `docs/adr/0001-no-generated-audio.md` | 音楽音源を生成・保存・配布しないという設計判断を記録した ADR。 |

## 現在の状態

- GitHub リポジトリ: <https://github.com/shinkai23/cross-subscription-music-timeline>
- iOS は SwiftUI ソース骨格まで作成済み。
- Backend は Fastify + Prisma の骨格、モック API、マッチング関数、CI 設定まで作成済み。
- この Windows 環境では `npm` と Xcode が利用できないため、Backend の型チェック・テスト、iOS ビルドは未実行です。
