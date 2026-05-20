# Cross-Subscription Music Timeline

Apple Music と Spotify の間にある「共有しにくさ」を減らすための、iOS 重視の音楽投稿・プレイリスト再現アプリです。

ユーザーは好きな曲、アルバム、自作プレイリストを紹介文付きで投稿できます。タイムラインでは投稿された音楽が並び、受け手は自分が利用しているサブスクリプションサービスで楽曲を開いたり、可能な範囲でプレイリストを再現したりできます。

## 概要

音楽配信サービスごとに、同じ楽曲であっても異なるIDが割り当てられます。

例えば、Spotify上のある曲とApple Music上の同じ曲は、それぞれ別のprovider track IDを持ちます。

このアプリでは、楽曲そのものを表す `tracks` と、Spotify / Apple Music 上の楽曲情報を表す `provider_tracks` を分離することで、異なるサービス上の同一楽曲をアプリケーション内で同じ楽曲として扱えるようにしています。

## 技術構成

- iOS: SwiftUI, MusicKit
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Auth: JWT
- Provider integration: Apple Music / Spotify adapter pattern
- Matching: ISRC 優先、曲名・アーティスト・アルバム・再生時間で補助
- Deploy: Docker + AWS ECS Fargate
- DB: Amazon RDS PostgreSQL
- Secrets: AWS Secrets Manager
- CI: GitHub Actions, Python, pytest, ruff

## 設計上の見どころ

- `tracks` と `provider_tracks` を分離し、同一楽曲をサービス横断で扱う
- `posts` は canonical `track_id` と投稿元の `source_provider_track_id` を保持する
- Apple Music / Spotify は adapter pattern で抽象化する
- Provider token は暗号化保存を前提とする
- DB schema は Alembic migration で管理する
- pytest / ruff による継続的な検証を行う
- AWS ECS Fargate / RDS / Secrets Manager を前提にした構成へ整理する

## プロダクトの核

このアプリの価値は、単なる音楽 SNS ではなく、**サービスをまたいだ音楽共有・プレイリスト再現**にあります。

例:

- Spotify ユーザーが楽曲や自作プレイリストを投稿する。
- Apple Music ユーザーがその投稿を見る。
- API が ISRC や曲名・アーティスト名を使って Apple Music 上の同じ曲を探す。
- Apple Music ユーザーは自分のサービス上で曲を開いたり、プレイリストを再現したりできる。

## 投稿と再生情報の流れ

投稿前に、クライアントは対象プロバイダーの楽曲再生情報を取得します。

```text
GET /providers/{provider}/tracks/{track_id}/playback
```

バックエンドはprovider APIから取得した情報をもとに、以下を保存します。

```text
tracks
  楽曲そのもの

provider_tracks
  Spotify / Apple Music 上の楽曲情報
```

その後、クライアントは投稿を作成します。

```text
POST /posts
```

リクエスト例:

```json
{
  "provider": "spotify",
  "provider_track_id": "spotify-track-1",
  "caption": "Great track"
}
```

バックエンドは `provider/provider_track_id` から `provider_tracks` を解決し、投稿には以下を保存します。

```text
posts.track_id
posts.source_provider_track_id
```

これにより、投稿は楽曲そのものを表す canonical `track_id` と、投稿元サービス上の楽曲情報を同時に参照できます。

## やらないこと

著作権と各サービスの規約を守るため、以下は明確に対象外です。

- 音源ファイルを生成、保存、アップロード、再配布しない。
- Spotify や Apple Music をスクレイピングしない。
- Spotify の 30 秒 preview URL のみを前提にした恒久的な再生設計にしない。
- 歌詞全文を投稿・保存しない。
- Spotify Content や Apple Music 由来のコンテンツを AI モデル学習に使わない。
- Apple、Apple Music、Spotify、アーティスト、レーベルから公認されたように見せない。

## リポジトリ構成

```text
apps/ios/              SwiftUI + MusicKit prototype
backend/api/           FastAPI + SQLAlchemy + Alembic API
backend/api_legacy/    旧 Fastify backend の退避先
docs/                  product, architecture, legal, provider design
infra/                 AWS ECS Fargate / RDS deployment notes
.github/workflows/     CI
docker-compose.yml     local PostgreSQL definition
```

既存の iOS SwiftUI prototype、法務・Provider リスク文書、Provider integration design は残しています。

## ローカル開発

PostgreSQLを起動します。

```bash
docker compose up -d postgres
```

Backendを起動します。

```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 4000
```

ヘルスチェック:

```bash
curl http://127.0.0.1:4000/health
```

期待値:

```json
{
  "status": "ok"
}
```

## テスト

Backendのlintとテストを実行します。

```bash
cd backend/api
ruff check .
pytest
```

DBを使うテストはSQLiteのin-memory databaseを使います。

本番・ローカル実行はPostgreSQLを使い、schema変更はAlembic migrationで管理します。

## ドキュメント

- [要件定義](docs/product-requirements.md)
- [ドメインモデル設計](docs/domain-model.md)
- [法務・外部 API リスク](docs/legal-and-platform-risk.md)
- [アーキテクチャ](docs/architecture.md)
- [Provider 連携設計](docs/provider-integration.md)
- [ローカル開発手順](docs/local-development.md)
- [AWS アーキテクチャ](infra/aws-architecture.md)
- [デプロイ手順](infra/deployment.md)
- [ロードマップ](docs/roadmap.md)

## 現在の状態

- iOS は SwiftUI prototype を保持。
- Backend は FastAPI + SQLAlchemy + Alembic + PostgreSQL 構成へ移行済み。
- JWT認証、ユーザー作成、投稿API、Provider adapter、Spotify OAuth、Apple Music連携基盤を実装。
- `tracks` / `provider_tracks` / `posts` による canonical track model を導入。
- タイムライン投稿に provider playback metadata を含める基盤を実装。
- pytest / ruff による検証を整備。
