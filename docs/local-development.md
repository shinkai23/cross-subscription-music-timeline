# Local Development

## Repository

The default branch is `main`.

```bash
git status
```

## Backend

The backend needs Node.js 22, npm, and Docker.

```bash
docker compose up -d postgres
cd backend/api
cp .env.example .env
npm install
npm run typecheck
npm test
npm run dev
```

Health check:

```bash
curl http://127.0.0.1:4000/health
```

## iOS

The iOS source skeleton is under `apps/ios/MusicTimelineApp`.

Because this workspace is on Windows, create and build the actual Xcode project on macOS:

1. Create a new iOS App project in Xcode.
2. Set the target name to `MusicTimelineApp`.
3. Copy the Swift files from `apps/ios/MusicTimelineApp`.
4. Add MusicKit capability.
5. Add the Apple Music usage description.
6. Build and run on a physical iPhone for MusicKit authorization testing.

## GitHub

Create the repository manually or with GitHub CLI on a machine that has `gh` installed.

```bash
git remote add origin https://github.com/<owner>/cross-subscription-music-timeline.git
git push -u origin main
```

