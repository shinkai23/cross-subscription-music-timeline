import SwiftUI

struct MusicSearchResultRow: View {
    let result: MusicSearchResult

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: result.artworkURL) { image in
                image
                    .resizable()
                    .scaledToFill()
            } placeholder: {
                RoundedRectangle(cornerRadius: 8)
                    .fill(.quaternary)
                    .overlay {
                        Image(systemName: result.itemType == .album ? "square.stack" : "music.note")
                            .foregroundStyle(.secondary)
                    }
            }
            .frame(width: 52, height: 52)
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(alignment: .leading, spacing: 4) {
                Text(result.title)
                    .font(.headline)
                    .lineLimit(1)

                Text(result.subtitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)

                Text(result.provider.displayName)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}

#Preview {
    MusicSearchResultRow(
        result: MusicSearchResult(
            id: "1",
            provider: .appleMusic,
            itemType: .song,
            title: "Cloud 9",
            subtitle: "Beach Bunny",
            artworkURL: nil,
            providerURL: nil,
            isrc: nil
        )
    )
}

