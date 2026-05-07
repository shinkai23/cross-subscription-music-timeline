# アーキテクチャ

## 全体像

```text
iOS App (SwiftUI + MusicKit)
  -> HTTPS
  -> Application Load Balancer
  -> ECS Fargate Service
  -> FastAPI
  -> SQLAlchemy
  -> Amazon RDS PostgreSQL
```

Secrets は AWS Secrets Manager で管理し、FastAPI container は ECS task definition の environment / secrets から `DATABASE_URL`、`JWT_SECRET`、Spotify keys、Apple Music keys を受け取ります。ログは CloudWatch Logs に送ります。

## Backend

Backend は `backend/api` に置きます。

- `app/main.py`: FastAPI application entrypoint
- `app/routers`: HTTP endpoint
- `app/services`: use case / business logic
- `app/repositories`: SQLAlchemy database access
- `app/models`: SQLAlchemy models
- `app/schemas`: Pydantic request / response schema
- `app/providers`: Apple Music / Spotify adapter pattern
- `app/matching`: cross-provider track matching
- `alembic`: database migration

## Provider Adapter

Apple Music と Spotify の差分は Backend 内の adapter interface に閉じ込めます。

```python
class MusicProviderAdapter:
    async def search_tracks(self, query: str, user_token: str | None = None): ...
    async def get_playlist(self, playlist_id: str, user_token: str | None = None): ...
    async def create_playlist(self, input_data, user_token: str): ...
    async def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str], user_token: str): ...
    def build_open_url(self, item): ...
```

## マッチング戦略

優先順位:

1. ISRC 完全一致
2. 曲名 + メインアーティスト + アルバム
3. 曲名 + メインアーティスト + 再生時間の近さ
4. バージョン表記を正規化した曲名
5. ユーザーが候補から選択

マッチング結果には、信頼度と理由を保存します。

## データモデル

- `users`: handle は unique
- `service_accounts`: provider + provider_user_id は unique
- `posts`: 投稿対象 Provider item と caption を保持
- `tracks`: provider + provider_track_id は unique、isrc は index
- `track_matches`: source_provider + source_track_id + target_provider は index
- `reports`: 投稿や対象 item の通報
- `playlists`: provider + provider_playlist_id は unique
- `playlist_items`: playlist_id + position は unique

## セキュリティ

- Auth は JWT を使う。
- Provider token は Backend で暗号化保存する。
- Spotify のモバイル認可は PKCE を使う。
- Apple Music の秘密鍵はサーバー側だけで扱う。
- Provider 権限 scope は最小限にする。
- アカウント連携解除とデータ削除導線を用意する。
