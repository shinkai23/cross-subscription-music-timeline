# ロードマップ

## Phase 0: 調査とプロジェクト初期化

- [x] プロダクトコンセプト分析
- [x] 法務・Provider リスク整理
- [x] 初期アーキテクチャ
- [x] GitHub テンプレート
- [x] GitHub Actions draft
- [ ] GitHub Project board 作成
- [ ] ロードマップから初期 Issue を作成

## Phase 1: iOS Apple Music プロトタイプ

- [x] iOS SwiftUI アプリ骨格を作成
- [x] MusicKit 認可の骨格を追加
- [x] Apple Music カタログ検索の骨格を追加
- [x] ローカルモックタイムラインを作成
- [ ] 曲・アルバムカードを実機で表示確認
- [ ] Backend API との接続

## Phase 2: Backend FastAPI MVP

- [x] Fastify backend を `backend/api_legacy` に退避
- [x] FastAPI service skeleton を作成
- [x] SQLAlchemy model foundation を追加
- [x] Alembic foundation を追加
- [x] `GET /health` を追加
- [x] `GET /posts` / `POST /posts` foundation を追加
- [x] Provider adapter interface を追加
- [x] matching foundation と単体テストを追加
- [x] 初期 Alembic migration を生成
- [ ] 投稿 CRUD を RDS PostgreSQL 前提で本実装
- [ ] JWT auth を router に接続

## Phase 3: Spotify / Apple Music 連携

- [ ] Spotify app を登録
- [ ] Spotify OAuth PKCE を実装
- [ ] Apple Music developer token 管理を実装
- [ ] ユーザーが選んだプレイリストを import
- [ ] 正規化したプレイリストメタデータを保存
- [ ] Provider deep link を開く

## Phase 4: サービス間マッチング

- [x] ISRC 優先の matching concept を Python に移植
- [x] title / artist / album / duration fallback を Python に移植
- [ ] Provider API 検索結果と matching service を接続
- [ ] confidence と reason を DB 保存
- [ ] プレイリスト変換レビュー UI を実機で確認

## Phase 5: AWS ECS Fargate Deploy

- [x] AWS architecture docs を追加
- [ ] Dockerfile を追加
- [ ] ECR repository を作成
- [ ] ECS cluster / service / task definition を作成
- [ ] RDS PostgreSQL を作成
- [ ] Secrets Manager に runtime secret を登録
- [ ] GitHub Actions deploy path を実装

## Phase 6: コンプライアンスとモデレーション

- [ ] 通報フロー
- [ ] ユーザーブロック
- [ ] 投稿削除
- [ ] 管理者向けモデレーション画面
- [ ] Provider 連携解除
- [ ] データ削除リクエスト導線
