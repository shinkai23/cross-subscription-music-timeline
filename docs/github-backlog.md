# GitHub Backlog

Create these as GitHub Issues after the remote repository is created.

## Milestone: Foundation

### 1. Confirm provider terms for MVP

Labels: `legal-risk`, `research`

Acceptance criteria:

- Apple Music API and MusicKit terms are reviewed.
- Spotify Developer Policy and Web API restrictions are reviewed.
- The README and legal risk document are updated with current links and decisions.

### 2. Create Xcode project and import SwiftUI shell

Labels: `feature`, `ios`

Acceptance criteria:

- Xcode project builds on latest stable Xcode.
- Files under `apps/ios/MusicTimelineApp` are imported.
- App launches to the timeline tab.

### 3. Add Apple Music capability and authorization

Labels: `feature`, `ios`, `apple-music`

Acceptance criteria:

- App requests MusicKit authorization.
- App shows authorized, denied, and restricted states.
- App checks Apple Music subscription status.

### 4. Implement Apple Music catalog search

Labels: `feature`, `ios`, `apple-music`

Acceptance criteria:

- User can search songs and albums.
- Results show title, artist, artwork, and provider link.
- Selected result can be used in a post draft.

### 5. Run backend API locally

Labels: `feature`, `backend`

Acceptance criteria:

- `GET /health` returns success.
- `GET /posts` returns mock timeline data.
- TypeScript typecheck passes in CI.

## Milestone: Playlist Conversion MVP

### 6. Implement Spotify OAuth PKCE

Labels: `feature`, `spotify`, `backend`

Acceptance criteria:

- User can connect Spotify with PKCE.
- Granted scopes are stored.
- Disconnect flow deletes provider account data.

### 7. Import a Spotify playlist

Labels: `feature`, `spotify`, `backend`

Acceptance criteria:

- User can paste or select a Spotify playlist.
- Backend stores normalized playlist metadata.
- Local files and unavailable tracks are marked clearly.

### 8. Implement ISRC matching

Labels: `feature`, `matching`

Acceptance criteria:

- Exact ISRC matches are marked as high confidence.
- Title/artist fallback is used only when ISRC is unavailable.
- Match reason and confidence are stored.

### 9. Build playlist conversion review UI

Labels: `feature`, `ios`, `matching`

Acceptance criteria:

- Matched, review-needed, and unavailable tracks are visually distinct.
- User can exclude unavailable or wrong matches.
- User must explicitly confirm before playlist creation.

### 10. Create Apple Music playlist from matched tracks

Labels: `feature`, `ios`, `apple-music`

Acceptance criteria:

- Confirmed tracks are written to a new Apple Music library playlist.
- Failures show actionable messages.
- Conversion result is recorded.

## Milestone: Safety

### 11. Add report and moderation data flow

Labels: `feature`, `moderation`

Acceptance criteria:

- User can report a post.
- Reports are stored with reason and details.
- Copyright reason is available.

### 12. Add AI text assistance guardrails

Labels: `feature`, `ai`, `legal-risk`

Acceptance criteria:

- AI only generates captions, tags, and summaries.
- Prompt rejects audio generation and full lyric requests.
- Source content used by AI is logged at a high level for audit.

