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
