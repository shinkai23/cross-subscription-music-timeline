# Backend API

Fastify API for the music timeline app.

## Local Setup

Requirements:

- Node.js 22
- npm
- Docker for PostgreSQL

```bash
cp .env.example .env
docker compose up -d postgres
npm install
npm run typecheck
npm test
npm run dev
```

The API listens on `http://127.0.0.1:4000` by default.

## Endpoints

- `GET /health`
- `GET /auth/providers`
- `POST /auth/provider-connections`
- `POST /auth/spotify/authorize-url`
- `GET /posts`
- `POST /posts`

## Provider Tokens

Provider token handling is intentionally incomplete. The implementation must add encrypted storage before real Apple Music or Spotify refresh tokens are persisted.

## Safety Constraints

- No raw audio storage.
- No full lyric storage.
- No scraping.
- No Spotify restricted endpoints for new functionality.
