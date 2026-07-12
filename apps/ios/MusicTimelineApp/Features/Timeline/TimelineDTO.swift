//
//  TimelineDTO.swift
//  MusicTimelineApp
//

import Foundation

struct TimelineResponse: Decodable {
    let items: [PostDTO]
    let nextBefore: String?

    enum CodingKeys: String, CodingKey {
        case items
        case nextBefore = "next_before"
    }
}

struct PostDTO: Decodable, Identifiable {
    let id: String
    let userId: String
    let trackId: String
    let sourceProviderTrackId: String
    let itemType: String
    let caption: String?
    let visibility: String
    let createdAt: String
    let playback: PlaybackDTO

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case trackId = "track_id"
        case sourceProviderTrackId = "source_provider_track_id"
        case itemType = "item_type"
        case caption
        case visibility
        case createdAt = "created_at"
        case playback
    }
}

struct PlaybackDTO: Decodable {
    let provider: String
    let providerTrackId: String
    let title: String
    let artistName: String
    let albumName: String?
    let durationMs: Int?
    let artworkUrl: String?
    let providerUrl: String?
    let previewUrl: String?
    let playbackId: String?
    let isPlayable: Bool
    let playbackMode: String?

    enum CodingKeys: String, CodingKey {
        case provider
        case providerTrackId = "provider_track_id"
        case title
        case artistName = "artist_name"
        case albumName = "album_name"
        case durationMs = "duration_ms"
        case artworkUrl = "artwork_url"
        case providerUrl = "provider_url"
        case previewUrl = "preview_url"
        case playbackId = "playback_id"
        case isPlayable = "is_playable"
        case playbackMode = "playback_mode"
    }
}

extension TimelineResponse {
    static let preview = TimelineResponse(
        items: [.spotifyPreview, .appleMusicExternal],
        nextBefore: nil
    )
}

extension PostDTO {
    static let spotifyPreview = PostDTO(
        id: "post-spotify-1",
        userId: "user-1",
        trackId: "track-1",
        sourceProviderTrackId: "provider-track-1",
        itemType: "track",
        caption: "30-second preview is available for this Spotify post.",
        visibility: "public",
        createdAt: "2026-07-09T00:00:00Z",
        playback: PlaybackDTO(
            provider: "spotify",
            providerTrackId: "spotify-track-1",
            title: "Preview Track",
            artistName: "Spotify Artist",
            albumName: "MVP Album",
            durationMs: 180000,
            artworkUrl: nil,
            providerUrl: "https://open.spotify.com/track/spotify-track-1",
            previewUrl: "https://example.com/preview.mp3",
            playbackId: "spotify-track-1",
            isPlayable: true,
            playbackMode: "preview"
        )
    )

    static let appleMusicExternal = PostDTO(
        id: "post-apple-1",
        userId: "user-2",
        trackId: "track-2",
        sourceProviderTrackId: "provider-track-2",
        itemType: "track",
        caption: "Apple Music stays external until MusicKit is introduced.",
        visibility: "public",
        createdAt: "2026-07-09T00:05:00Z",
        playback: PlaybackDTO(
            provider: "apple_music",
            providerTrackId: "apple-track-1",
            title: "External Track",
            artistName: "Apple Artist",
            albumName: "Future MusicKit",
            durationMs: 210000,
            artworkUrl: nil,
            providerUrl: "https://music.apple.com/song/apple-track-1",
            previewUrl: nil,
            playbackId: "apple-track-1",
            isPlayable: true,
            playbackMode: "external"
        )
    )
}
