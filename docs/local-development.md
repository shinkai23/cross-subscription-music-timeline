# ローカル開発

## Backend

Backend は FastAPI, SQLAlchemy, Alembic, PostgreSQL で構成します。

必要なもの:

- Python 3.12
- Docker

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

Alembic migration:

```bash
cd backend/api
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## iOS

iOS の SwiftUI prototype は `apps/ios` にあります。MusicKit capability と Apple Music 利用目的の説明文を Xcode 側で設定して、実機 iPhone で認可を確認します。
