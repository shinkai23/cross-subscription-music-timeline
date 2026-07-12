//
//  TrackSearchDTO.swift
//  MusicTimelineApp
//

import Foundation

struct TrackSearchResultDTO: Decodable, Identifiable, Hashable {
    var id: String {
        "\(provider):\(providerTrackId)"
    }

    let provider: String
    let providerTrackId: String
    let title: String
    let artistName: String
    let albumName: String?
    let durationMs: Int?
    let artworkUrl: String?
    let providerUrl: String?

    enum CodingKeys: String, CodingKey {
        case provider
        case providerTrackId = "provider_track_id"
        case title
        case artistName = "artist_name"
        case albumName = "album_name"
        case durationMs = "duration_ms"
        case artworkUrl = "artwork_url"
        case providerUrl = "provider_url"
    }
}

enum SearchProvider: String, CaseIterable, Identifiable {
    case spotify
    case appleMusic = "apple_music"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .spotify:
            return "Spotify"
        case .appleMusic:
            return "Apple Music"
        }
    }
}

extension TrackSearchResultDTO {
    static let previewSpotify = TrackSearchResultDTO(
        provider: "spotify",
        providerTrackId: "spotify-track-1",
        title: "Preview Track",
        artistName: "Spotify Artist",
        albumName: "MVP Album",
        durationMs: 180000,
        artworkUrl: nil,
        providerUrl: "https://open.spotify.com/track/spotify-track-1"
    )

    static let previewAppleMusic = TrackSearchResultDTO(
        provider: "apple_music",
        providerTrackId: "apple-track-1",
        title: "External Track",
        artistName: "Apple Artist",
        albumName: "Future MusicKit",
        durationMs: 210000,
        artworkUrl: nil,
        providerUrl: "https://music.apple.com/song/apple-track-1"
    )
}
