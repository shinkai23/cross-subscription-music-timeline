import Foundation

struct MusicSearchResult: Identifiable {
    let id: String
    let provider: MusicProvider
    let itemType: MusicItemType
    let title: String
    let subtitle: String
    let artworkURL: URL?
    let providerURL: URL?
    let isrc: String?
}

