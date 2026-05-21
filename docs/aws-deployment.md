# AWS手動デプロイ手順

## 目的

FastAPI backend を AWS ECS Fargate に手動デプロイする。

最初は学習と動作確認を優先し、Terraform / CDK / GitHub Actions deploy は使わない。

## 構成

```text
Client
  -> Application Load Balancer
  -> ECS Fargate
  -> FastAPI container
  -> RDS PostgreSQL

ECS Fargate
  -> Secrets Manager
  -> CloudWatch Logs

Docker image
  -> Amazon ECR
```

## 今回使った値

```text
AWS account ID: 631069968321
Region: us-east-1
App name: music-timeline-api
RDS endpoint: music-timeline-db.cu7c6866m1cf.us-east-1.rds.amazonaws.com
RDS port: 5432
RDS database: postgres
RDS username: postgres
ALB DNS: music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com
```

## 前提

- AWS CLI が設定済み
- Docker Desktop が起動している
- 作業ディレクトリはリポジトリルート

```bash
aws sts get-caller-identity
docker info
```

環境変数:

```bash
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=631069968321
export APP_NAME=music-timeline-api
```

## 1. ECR repositoryを作成

Docker image の保存先を作る。

```bash
aws ecr create-repository \
  --repository-name "${APP_NAME}" \
  --region "${AWS_REGION}"
```

作成済みの場合は次へ進む。

## 2. Docker imageをbuildしてECRへpush

ECRへログインする。

```bash
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login \
    --username AWS \
    --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
```

imageをbuildする。

```bash
docker buildx build \
  --platform linux/amd64 \
  -t "${APP_NAME}:latest" \
  --load \
  ./backend/api
```

`--load` を付けないと、buildx がローカルの `docker images` にimageを残さない場合がある。

tagを付ける。

```bash
docker tag \
  "${APP_NAME}:latest" \
  "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:latest"
```

pushする。

```bash
docker push \
  "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:latest"
```

zshでは `$APP_NAME:latest` のような書き方が意図せず壊れることがあるため、`${APP_NAME}:latest` の形式を使う。

## 3. RDS PostgreSQLを作成

AWS Consoleで作成する。

推奨設定:

- Service: Aurora and RDS
- Engine: PostgreSQL
- DB instance identifier: `music-timeline-db`
- Master username: `postgres`
- DB name: `postgres`
- Port: `5432`
- Credentials management: Secrets Manager
- Public access: `No`
- VPC: ECS / ALB と同じVPC
- Security Group: 後でECSから5432を許可する

RDS作成後、以下を控える。

```text
Endpoint: music-timeline-db.cu7c6866m1cf.us-east-1.rds.amazonaws.com
Port: 5432
Database: postgres
Username: postgres
```

アプリ用の `DATABASE_URL` は以下の形式にする。

```text
postgresql+psycopg://postgres:<password>@music-timeline-db.cu7c6866m1cf.us-east-1.rds.amazonaws.com:5432/postgres
```

RDSのpasswordは、RDSが自動作成したSecrets Manager secretから確認する。

## 4. Secrets Managerにアプリ用secretを作成

RDS用secretとは別に、アプリ用secretを作る。

Secret名:

```text
music-timeline/prod/api
```

Secret value:

```json
{
  "DATABASE_URL": "postgresql+psycopg://postgres:<password>@music-timeline-db.cu7c6866m1cf.us-east-1.rds.amazonaws.com:5432/postgres",
  "JWT_SECRET": "<strong-random-secret>",
  "ENVIRONMENT": "production",
  "JWT_ALGORITHM": "HS256",
  "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
  "SPOTIFY_CLIENT_ID": "",
  "SPOTIFY_REDIRECT_URI": "http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com/auth/spotify/callback",
  "SPOTIFY_AUTH_SCOPES": "playlist-read-private playlist-modify-private playlist-modify-public",
  "TOKEN_ENCRYPTION_KEY": "<fernet-key>",
  "APPLE_MUSIC_DEVELOPER_TOKEN": "",
  "APPLE_MUSIC_STOREFRONT": "jp"
}
```

Fernet key:

```bash
cd backend/api
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

JWT secret:

```bash
openssl rand -hex 32
```

## 5. Security Groupを作成

ALB用とECS用は分ける。

### ALB Security Group

例:

```text
music-timeline-alb-sg
sg-0d17f6cd7545f9082
```

Inbound:

| Type | Port | Source |
|---|---:|---|
| HTTP | 80 | `0.0.0.0/0` |

Outbound:

| Type | Port | Destination |
|---|---:|---|
| All traffic | All | `0.0.0.0/0` |

### ECS Security Group

例:

```text
music-timeline-ecs-sg
sg-036d6a2cd4ada2cc3
```

Inbound:

| Type | Port | Source |
|---|---:|---|
| Custom TCP | 4000 | ALB Security Group |

Outbound:

| Type | Port | Destination |
|---|---:|---|
| All traffic | All | `0.0.0.0/0` |

### RDS Security Group

RDSに紐づいているSecurity Groupへ追加する。

Inbound:

| Type | Port | Source |
|---|---:|---|
| PostgreSQL | 5432 | ECS Security Group |

今回のRDSはdefault Security Groupに紐づいていたため、default Security Groupに `5432 from sg-036d6a2cd4ada2cc3` を追加した。

## 6. IAM roleを作成

ECS task execution roleを作成する。

Role名:

```text
ecsTaskExecutionRole
```

付与するmanaged policy:

```text
AmazonECSTaskExecutionRolePolicy
```

Secrets Managerを読むため、inline policyを追加する。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:631069968321:secret:music-timeline/prod/api-*"
    }
  ]
}
```

## 7. CloudWatch Logs groupを作成

```bash
aws logs create-log-group \
  --log-group-name /ecs/music-timeline-api \
  --region "${AWS_REGION}"
```

作成済みの場合は次へ進む。

## 8. ECS Clusterを作成

```bash
aws ecs create-cluster \
  --cluster-name music-timeline-cluster \
  --region "${AWS_REGION}"
```

## 9. ECS Task Definitionを登録

`task-definition.json` を一時的に作る。

`<secret-arn>` は `aws secretsmanager describe-secret` で取得した実際のARNに置き換える。

```bash
aws secretsmanager describe-secret \
  --secret-id music-timeline/prod/api \
  --region "${AWS_REGION}"
```

Task Definition例:

```json
{
  "family": "music-timeline-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::631069968321:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "631069968321.dkr.ecr.us-east-1.amazonaws.com/music-timeline-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 4000,
          "protocol": "tcp"
        }
      ],
      "secrets": [
        { "name": "DATABASE_URL", "valueFrom": "<secret-arn>:DATABASE_URL::" },
        { "name": "JWT_SECRET", "valueFrom": "<secret-arn>:JWT_SECRET::" },
        { "name": "ENVIRONMENT", "valueFrom": "<secret-arn>:ENVIRONMENT::" },
        { "name": "JWT_ALGORITHM", "valueFrom": "<secret-arn>:JWT_ALGORITHM::" },
        { "name": "ACCESS_TOKEN_EXPIRE_MINUTES", "valueFrom": "<secret-arn>:ACCESS_TOKEN_EXPIRE_MINUTES::" },
        { "name": "SPOTIFY_CLIENT_ID", "valueFrom": "<secret-arn>:SPOTIFY_CLIENT_ID::" },
        { "name": "SPOTIFY_REDIRECT_URI", "valueFrom": "<secret-arn>:SPOTIFY_REDIRECT_URI::" },
        { "name": "SPOTIFY_AUTH_SCOPES", "valueFrom": "<secret-arn>:SPOTIFY_AUTH_SCOPES::" },
        { "name": "TOKEN_ENCRYPTION_KEY", "valueFrom": "<secret-arn>:TOKEN_ENCRYPTION_KEY::" },
        { "name": "APPLE_MUSIC_DEVELOPER_TOKEN", "valueFrom": "<secret-arn>:APPLE_MUSIC_DEVELOPER_TOKEN::" },
        { "name": "APPLE_MUSIC_STOREFRONT", "valueFrom": "<secret-arn>:APPLE_MUSIC_STOREFRONT::" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/music-timeline-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

登録する。

```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region "${AWS_REGION}"
```

登録後、`task-definition.json` は削除してよい。secret値は含まないが、account IDやsecret ARNを含むためcommitしない。

## 10. ALBを作成

AWS Consoleで作成する。

推奨設定:

- Type: Application Load Balancer
- Scheme: Internet-facing
- Listener: HTTP 80
- VPC: RDSと同じVPC
- Subnet: public subnetを2つ以上
- Security Group: ALB Security Group
- Target group type: IP
- Target group protocol: HTTP
- Target group port: 4000
- Health check path: `/health`

今回のALB:

```text
music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com
```

注意:

ECS Serviceで選ぶsubnetは、ALBで有効化したAZに合わせる。

今回ALBで有効だったsubnet:

```text
subnet-013d654a19edc8092
subnet-017cc7e3195a69a24
```

ECS Serviceにそれ以外のsubnetを含めると、Target Groupで以下のようにunhealthyになる。

```text
Target is in an Availability Zone that is not enabled for the load balancer
```

## 11. ECS Serviceを作成

AWS Consoleで作成する。

推奨設定:

- Cluster: `music-timeline-cluster`
- Launch type: Fargate
- Task definition: `music-timeline-api`
- Service name: `music-timeline-api-service`
- Desired tasks: `1`
- Networking:
  - VPC: RDS / ALB と同じVPC
  - Subnets: ALBで有効化したpublic subnet
  - Public IP: Enabled
  - Security Group: ECS Security Group
- Load balancer:
  - ALB: 作成済みALB
  - Target group: 作成済みtarget group
  - Container: `api:4000`

Health check grace periodは、指定できる場合は60秒にする。画面に出ない場合は作成後にCLIで設定する。

```bash
aws ecs update-service \
  --cluster music-timeline-cluster \
  --service music-timeline-api-service \
  --health-check-grace-period-seconds 60 \
  --region "${AWS_REGION}"
```

ECS Service作成後にnetwork設定を修正する場合:

```bash
aws ecs update-service \
  --cluster music-timeline-cluster \
  --service music-timeline-api-service \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-013d654a19edc8092,subnet-017cc7e3195a69a24],securityGroups=[sg-036d6a2cd4ada2cc3],assignPublicIp=ENABLED}' \
  --health-check-grace-period-seconds 60 \
  --force-new-deployment \
  --region "${AWS_REGION}"
```

## 12. 動作確認

ALB DNS nameでhealth checkを叩く。

```bash
curl http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com/health
```

期待値:

```json
{"status":"ok"}
```

DBを使うAPIも確認する。

```bash
curl http://music-timeline-api-alb-904044250.us-east-1.elb.amazonaws.com/posts
```

期待値:

```json
{"items":[],"next_before":null}
```

CloudWatch Logs:

```bash
aws logs tail /ecs/music-timeline-api \
  --follow \
  --region "${AWS_REGION}"
```

## 13. Alembic migrationをECS one-off taskで実行

RDSがprivateの場合、ローカルPCから直接 `alembic upgrade head` できない。

そのため、migration用Task Definitionを一時的に登録して実行する。

`task-definition-migrate.json` は通常のTask Definitionをコピーし、以下だけ変更する。

```json
{
  "family": "music-timeline-api-migrate",
  "containerDefinitions": [
    {
      "name": "api",
      "command": ["alembic", "upgrade", "head"]
    }
  ]
}
```

登録する。

```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition-migrate.json \
  --region "${AWS_REGION}"
```

one-off taskを実行する。

```bash
aws ecs run-task \
  --cluster music-timeline-cluster \
  --task-definition music-timeline-api-migrate:1 \
  --launch-type FARGATE \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-013d654a19edc8092,subnet-017cc7e3195a69a24],securityGroups=[sg-036d6a2cd4ada2cc3],assignPublicIp=ENABLED}' \
  --region "${AWS_REGION}"
```

停止まで待つ。

```bash
aws ecs wait tasks-stopped \
  --cluster music-timeline-cluster \
  --tasks <migration-task-arn> \
  --region "${AWS_REGION}"
```

終了コードを確認する。

```bash
aws ecs describe-tasks \
  --cluster music-timeline-cluster \
  --tasks <migration-task-arn> \
  --region "${AWS_REGION}"
```

`exitCode` が `0` なら成功。

ログ確認:

```bash
aws logs tail /ecs/music-timeline-api \
  --since 10m \
  --region "${AWS_REGION}"
```

今回のmigrationは以下まで成功した。

```text
initial schema
add track playback metadata
add provider tracks
normalize tracks and provider tracks
normalize posts to canonical tracks
```

実行後、`task-definition-migrate.json` は削除してよい。

## 14. 再デプロイ手順

コード変更後は、imageをbuildしてpushする。

```bash
docker buildx build \
  --platform linux/amd64 \
  -t "${APP_NAME}:latest" \
  --load \
  ./backend/api

docker tag \
  "${APP_NAME}:latest" \
  "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:latest"

docker push \
  "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}:latest"
```

ECS Serviceを再起動する。

```bash
aws ecs update-service \
  --cluster music-timeline-cluster \
  --service music-timeline-api-service \
  --force-new-deployment \
  --region "${AWS_REGION}"
```

## 15. 削除手順

検証後に不要なら削除する。

削除順:

1. ECS Service desired countを0にする
2. ECS Serviceを削除
3. ALBを削除
4. Target Groupを削除
5. ECS Clusterを削除
6. RDSを削除
7. Secrets Manager secretを削除
8. ECR repositoryを削除
9. CloudWatch Logs groupを削除

RDSとALBは課金されやすいため、検証後に放置しない。

## 次に自動化するもの

手動デプロイで `/health` と `/posts` が通った後に自動化する。

- GitHub ActionsでECR push
- GitHub ActionsでECS Service更新
- Alembic migration用one-off ECS task
- 独自ドメインとHTTPS
- TerraformまたはCDKによるIaC化
