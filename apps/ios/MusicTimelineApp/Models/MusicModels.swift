import Foundation

enum MusicProvider: String, CaseIterable, Identifiable {
    case appleMusic = "apple_music"
    case spotify = "spotify"

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .appleMusic:
            return "Apple Music"
        case .spotify:
            return "Spotify"
        }
    }
}

enum MusicItemType: String, Identifiable {
    case song
    case album
    case playlist

    var id: String { rawValue }
}

struct UserProfile: Identifiable {
    let id: UUID
    var displayName: String
    var handle: String
    var primaryProvider: MusicProvider
}

struct MusicPost: Identifiable {
    let id: UUID
    let author: UserProfile
    let itemType: MusicItemType
    let sourceProvider: MusicProvider
    let title: String
    let subtitle: String
    let caption: String
    let artworkURL: URL?
    let providerURL: URL?
    let tags: [String]
    let matchSummary: MatchSummary?
    let createdAt: Date
}

struct MatchSummary {
    let targetProvider: MusicProvider
    let matchedCount: Int
    let totalCount: Int
    let needsReviewCount: Int

    var displayText: String {
        if totalCount == 0 {
            return "No tracks"
        }

        return "\(matchedCount)/\(totalCount) matched"
    }
}

struct PlaylistConversionItem: Identifiable {
    enum State {
        case matched
        case needsReview
        case unavailable
    }

    let id: UUID
    let position: Int
    let sourceTitle: String
    let sourceArtist: String
    let matchedTitle: String?
    let matchedArtist: String?
    let state: State
}

