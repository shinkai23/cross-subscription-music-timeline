# Backend API

FastAPI, SQLAlchemy, Alembic, PostgreSQL を使う Backend API です。

現在は曲投稿・試聴タイムラインのMVP基盤として、JWT認証、Provider連携基盤、再生メタデータ取得、canonical track model、投稿API、タイムライン取得を実装しています。

検証用Backend API:

```text
http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com
```

AWS ECS Fargate 上で `/health`、`/posts`、Alembic migration、RDS PostgreSQL 接続を確認済みです。

## 技術構成

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- pytest
- ruff

## ローカル起動

リポジトリルートで PostgreSQL を起動します。

```bash
docker compose up -d postgres
```

Backend を起動します。

```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 4000
```

## 確認

Local:

```bash
curl http://127.0.0.1:4000/health
curl http://127.0.0.1:4000/posts
```

AWS:

```bash
curl http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com/health
curl http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com/posts
```

期待値:

```text
GET /health -> {"status":"ok"}
GET /posts  -> {"items":[],"next_before":null}
```

## テストと lint

```bash
cd backend/api
ruff check .
pytest
```

DB を使うテストは SQLite の in-memory database を使います。FastAPI の DB dependency を pytest fixture で差し替え、各テストごとに schema を作成・破棄します。

本番・ローカル実行は PostgreSQL を使います。Provider playback 取得から投稿作成、タイムライン取得までの中核フローは統合テストで検証しています。

## 構成

```text
app/
  core/           settings
  db/             SQLAlchemy session and metadata
  models/         SQLAlchemy models
  schemas/        Pydantic schemas
  repositories/   database access
  services/       use case layer
  routers/        FastAPI routers
  providers/      Apple Music / Spotify adapter pattern
  matching/       track matching
alembic/          migrations
tests/            pytest
```

## 安全制約

- 音楽音源を保存しない。
- 歌詞全文を保存しない。
- Spotify / Apple Music をスクレイピングしない。
- Provider token は暗号化して保存する。
