# AWS アーキテクチャ

## 構成

```text
iOS App
  -> HTTPS
  -> Application Load Balancer
  -> ECS Fargate Service
  -> FastAPI container
  -> Amazon RDS PostgreSQL
```

Backend は Docker image として Amazon ECR に push し、ECS Fargate の task definition から起動します。外部公開は ALB 経由に限定し、ECS task は private subnet に置く想定です。

## Secrets

AWS Secrets Manager に以下を保存します。

- `DATABASE_URL`
- `JWT_SECRET`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `APPLE_MUSIC_TEAM_ID`
- `APPLE_MUSIC_KEY_ID`
- `APPLE_MUSIC_PRIVATE_KEY`

ECS task role / execution role には必要な secret 読み取り権限だけを付与します。

## Observability

- ECS container logs は CloudWatch Logs に送る。
- ALB access logs は必要に応じて S3 に保存する。
- RDS は automated backup と CloudWatch metrics を有効にする。

## Network

- Public subnet: ALB
- Private subnet: ECS Fargate tasks, RDS PostgreSQL
- Security group: ALB から ECS の 4000 番へ、ECS から RDS の 5432 番へ許可

