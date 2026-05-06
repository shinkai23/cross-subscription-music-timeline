import Foundation
import MusicKit

struct AppleMusicCatalogService {
    func search(term: String) async throws -> [MusicSearchResult] {
        var request = MusicCatalogSearchRequest(
            term: term,
            types: [Song.self, Album.self]
        )
        request.limit = 10

        let response = try await request.response()

        let songs = response.songs.map { song in
            MusicSearchResult(
                id: song.id.rawValue,
                provider: .appleMusic,
                itemType: .song,
                title: song.title,
                subtitle: song.artistName,
                artworkURL: song.artwork?.url(width: 160, height: 160),
                providerURL: song.url,
                isrc: song.isrc
            )
        }

        let albums = response.albums.map { album in
            MusicSearchResult(
                id: album.id.rawValue,
                provider: .appleMusic,
                itemType: .album,
                title: album.title,
                subtitle: album.artistName,
                artworkURL: album.artwork?.url(width: 160, height: 160),
                providerURL: album.url,
                isrc: nil
            )
        }

        return Array(songs + albums)
    }
}

