# Backend API

音楽タイムラインアプリ用の Fastify API です。

## ローカルセットアップ

必要なもの:

- Node.js 22
- npm
- Docker

```bash
cp .env.example .env
docker compose up -d postgres
npm install
npm run typecheck
npm test
npm run dev
```

標準では `http://127.0.0.1:4000` で起動します。

## エンドポイント

- `GET /health`
- `GET /auth/providers`
- `POST /auth/provider-connections`
- `POST /auth/spotify/authorize-url`
- `GET /posts`
- `POST /posts`

## Provider トークン

Provider のトークン保存はまだ本実装ではありません。Apple Music や Spotify の refresh token を保存する前に、暗号化保存と削除導線を実装する必要があります。

## 安全制約

- 音楽音源を保存しない。
- 歌詞全文を保存しない。
- スクレイピングをしない。
- 新規機能で Spotify の制限対象 API に依存しない。
