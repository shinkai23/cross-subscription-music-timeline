# Cross-Subscription Music Timeline

Apple Music と Spotify の間にある「共有しにくさ」を減らすための、iOS 重視の音楽投稿・プレイリスト再現アプリです。

ユーザーは好きな曲、アルバム、自作プレイリストを紹介文付きで投稿できます。タイムラインでは投稿された音楽が並び、受け手は自分が選んだサブスクリプションで開いたり、可能な範囲でプレイリストを再現したりできます。

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

## プロダクトの核

このアプリの価値は、単なる音楽 SNS ではなく、**サービスをまたいだプレイリスト共有・再現**にあります。

例:

- Spotify ユーザーが自作プレイリストを投稿する。
- Apple Music ユーザーがその投稿を見る。
- API が ISRC や曲名・アーティスト名を使って Apple Music 上の同じ曲を探す。
- ユーザーが確認したうえで Apple Music にプレイリストを作成する。

## やらないこと

著作権と各サービスの規約を守るため、以下は明確に対象外です。

- 音源ファイルを生成、保存、アップロード、再配布しない。
- Spotify や Apple Music をスクレイピングしない。
- Spotify の 30 秒 preview URL に依存しない。
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

```bash
docker compose up -d postgres
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
ruff check .
pytest
uvicorn app.main:app --reload --host 0.0.0.0 --port 4000
```

ヘルスチェック:

```bash
curl http://127.0.0.1:4000/health
```

## ドキュメント

- [要件定義](docs/product-requirements.md)
- [法務・外部 API リスク](docs/legal-and-platform-risk.md)
- [アーキテクチャ](docs/architecture.md)
- [Provider 連携設計](docs/provider-integration.md)
- [ローカル開発手順](docs/local-development.md)
- [AWS アーキテクチャ](infra/aws-architecture.md)
- [デプロイ手順](infra/deployment.md)
- [ロードマップ](docs/roadmap.md)

## 現在の状態

- iOS は SwiftUI prototype を保持。
- Backend は FastAPI + SQLAlchemy + Alembic + PostgreSQL の skeleton へ移行済み。
- `GET /health`、投稿 API foundation、Provider adapter foundation、track matching foundation を追加済み。
