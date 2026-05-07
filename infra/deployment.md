# デプロイ

## 前提

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Container: Docker
- Runtime: AWS ECS Fargate
- Image registry: Amazon ECR
- Database: Amazon RDS PostgreSQL
- Secrets: AWS Secrets Manager

## GitHub Actions の流れ

1. Python 3.12 をセットアップする。
2. `backend/api/requirements.txt` を install する。
3. `ruff check .` を実行する。
4. `pytest` を実行する。
5. Docker image を build する。
6. Amazon ECR に push する。
7. ECS task definition の image tag を更新する。
8. ECS service を deploy する。

## Runtime secret

ECS task definition では Secrets Manager から以下を注入します。

- `DATABASE_URL`
- `JWT_SECRET`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `APPLE_MUSIC_TEAM_ID`
- `APPLE_MUSIC_KEY_ID`
- `APPLE_MUSIC_PRIVATE_KEY`

## Migration

Alembic migration は deploy と分離して実行します。初期運用では one-off ECS task で以下を実行します。

```bash
alembic upgrade head
```

本番では migration 実行権限と application runtime 権限を分ける方針にします。
