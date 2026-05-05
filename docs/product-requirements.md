# Product Requirements

## Problem

Music recommendations are fragmented by subscription service. A Spotify user may publish a playlist that an Apple Music user cannot easily recreate. Existing sharing usually stops at a link, which is weak when the receiver uses a different service.

## Goal

Build a mobile-first app where users post songs, albums, and playlists with personal context, and receivers can open or recreate that music in their own selected subscription service.

## Target Users

- Music fans who share playlists with friends.
- Apple Music users who often receive Spotify links.
- Spotify users who want their playlists to be understandable outside Spotify.
- Developers/recruiters reviewing this as a portfolio project.

## MVP User Stories

1. As a user, I can choose Apple Music or Spotify as my primary service.
2. As a user, I can connect Apple Music on iOS and grant only the permissions needed.
3. As a user, I can connect Spotify using OAuth PKCE.
4. As a user, I can search for a song, album, or playlist from a supported service.
5. As a user, I can post a music item with a short introduction.
6. As a user, I can browse a timeline of posts from people I follow.
7. As a user, I can tap a post and open it in my preferred service.
8. As a user, I can recreate a posted playlist in my preferred service when matching succeeds.
9. As a user, I can review unmatched or ambiguous tracks before creating a playlist.
10. As a user, I can report copyright, abuse, spam, or misleading posts.

## Timeline Card

Each post should show:

- Author
- Music type: song, album, playlist
- Title
- Artist or playlist owner
- Cover art from official provider where allowed
- Short recommendation text
- AI-assisted tags if accepted by the user
- Match status for the current user's service
- Primary action: open in selected service
- Secondary action: recreate playlist, save, like, comment, report

## Playlist Recreation Flow

1. User opens a playlist post.
2. Backend loads stored source playlist metadata.
3. Matching service attempts target-service matches.
4. UI shows:
   - matched tracks
   - candidate tracks
   - unavailable tracks
5. User confirms.
6. App creates a playlist using the target service API.
7. App writes a conversion result record for debugging and product metrics.

## AI Scope

Allowed:

- Draft a recommendation caption from user notes.
- Generate tags from metadata and the user's text.
- Summarize a playlist's mood based on track names, artists, genres, and user-provided text.
- Suggest post templates.

Not allowed:

- Generate a soundalike clip.
- Recreate a copyrighted melody.
- Train on Spotify Content or Apple Music content.
- Analyze raw service audio.
- Generate lyrics in the style of a specific artist.

## Success Metrics

- Playlist match rate.
- Playlist creation success rate.
- Number of posts with cross-service opens.
- Report rate.
- Percentage of users who connect a service.
- Time from opening a post to playing or saving music.

