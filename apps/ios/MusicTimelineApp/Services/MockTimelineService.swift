import Foundation

struct MockTimelineService {
    static let currentUser = UserProfile(
        id: UUID(),
        displayName: "Mame",
        handle: "mame",
        primaryProvider: .appleMusic
    )

    static let posts: [MusicPost] = [
        MusicPost(
            id: UUID(),
            author: UserProfile(
                id: UUID(),
                displayName: "Aki",
                handle: "aki",
                primaryProvider: .spotify
            ),
            itemType: .playlist,
            sourceProvider: .spotify,
            title: "Late Night Walk",
            subtitle: "18 tracks",
            caption: "Quiet tracks for walking home after the last train.",
            artworkURL: nil,
            providerURL: URL(string: "https://open.spotify.com/"),
            tags: ["night", "walk", "calm"],
            matchSummary: MatchSummary(
                targetProvider: .appleMusic,
                matchedCount: 16,
                totalCount: 18,
                needsReviewCount: 2
            ),
            createdAt: Date()
        ),
        MusicPost(
            id: UUID(),
            author: UserProfile(
                id: UUID(),
                displayName: "Rin",
                handle: "rin",
                primaryProvider: .appleMusic
            ),
            itemType: .album,
            sourceProvider: .appleMusic,
            title: "Blue Weekend",
            subtitle: "Wolf Alice",
            caption: "An album that changes shape depending on the time of day.",
            artworkURL: nil,
            providerURL: URL(string: "https://music.apple.com/"),
            tags: ["album", "guitar"],
            matchSummary: nil,
            createdAt: Date()
        )
    ]

    static let conversionItems: [PlaylistConversionItem] = [
        PlaylistConversionItem(
            id: UUID(),
            position: 1,
            sourceTitle: "Track One",
            sourceArtist: "Sample Artist",
            matchedTitle: "Track One",
            matchedArtist: "Sample Artist",
            state: .matched
        ),
        PlaylistConversionItem(
            id: UUID(),
            position: 2,
            sourceTitle: "Live Version",
            sourceArtist: "Sample Band",
            matchedTitle: "Live Version - Remastered",
            matchedArtist: "Sample Band",
            state: .needsReview
        ),
        PlaylistConversionItem(
            id: UUID(),
            position: 3,
            sourceTitle: "Local File",
            sourceArtist: "Unknown",
            matchedTitle: nil,
            matchedArtist: nil,
            state: .unavailable
        )
    ]
}

