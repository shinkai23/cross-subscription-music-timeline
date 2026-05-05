# Cross-Subscription Music Timeline

iOS first music sharing app concept for posting favorite songs, albums, and playlists, then opening or recreating them on the listener's preferred subscription service.

## Product Focus

The core value is not generic music SNS posting. The app should make a Spotify playlist understandable and reproducible for an Apple Music user, and the reverse later.

MVP priorities:

1. Post songs, albums, and playlists with a short recommendation text.
2. Show a timeline of music posts with official metadata and service links.
3. Let each user choose a primary listening service.
4. Match tracks across Apple Music and Spotify, prioritizing ISRC.
5. Recreate supported playlists in the user's selected service with explicit user authorization.
6. Use AI only for text assistance such as summaries, tags, and recommendation drafts.

## Non-Goals

- Do not generate, store, upload, or redistribute music audio.
- Do not scrape streaming services.
- Do not rely on Spotify 30-second preview URLs for new development.
- Do not post full lyrics.
- Do not imply endorsement by Apple, Apple Music, Spotify, artists, labels, or rightsholders.

## Initial Stack

- iOS: SwiftUI, MusicKit, Apple Music API
- Android: Kotlin, Jetpack Compose, phased after iOS MVP
- Backend: TypeScript, Fastify or NestJS, PostgreSQL, Prisma
- Jobs: metadata refresh and playlist matching workers
- GitHub: Issues, Projects, PR templates, GitHub Actions

## Documentation

- [Product Requirements](docs/product-requirements.md)
- [Legal and Platform Risk](docs/legal-and-platform-risk.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [ADR 0001: Do not generate or host music audio](docs/adr/0001-no-generated-audio.md)

