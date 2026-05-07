# Backend API

FastAPI, SQLAlchemy, Alembic, PostgreSQL を使う Backend API です。

現在は foundation 段階で、health check、投稿 API の基盤、Provider Adapter の基盤、楽曲マッチング基盤、初期 Alembic migration まで実装しています。

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

```bash
curl http://127.0.0.1:4000/health
curl http://127.0.0.1:4000/posts
```

期待値:

```text
GET /health -> {"status":"ok"}
GET /posts  -> []
```

## テストと lint

```bash
cd backend/api
ruff check .
pytest
```

DB を使うテストは SQLite の in-memory database を使います。FastAPI の DB dependency を pytest fixture で差し替え、各テストごとに schema を作成・破棄します。

本番・ローカル実行は PostgreSQL を使います。PostgreSQL 固有の挙動を検証する integration test は、provider 連携と migration 運用が固まった段階で追加します。

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
  providers/      Apple Music / Spotify adapter foundation
  matching/       track matching foundation
alembic/          migrations
tests/            pytest
```

## 安全制約

- 音楽音源を保存しない。
- 歌詞全文を保存しない。
- Spotify / Apple Music をスクレイピングしない。
- Provider token は暗号化保存と削除導線を実装してから扱う。
