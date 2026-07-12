//
//  TrackSearchResultRow.swift
//  MusicTimelineApp
//

import SwiftUI

struct TrackSearchResultRow: View {
    let track: TrackSearchResultDTO

    var body: some View {
        HStack(spacing: 12) {
            artwork

            VStack(alignment: .leading, spacing: 4) {
                Text(track.title)
                    .font(.headline)
                    .lineLimit(2)
                Text(track.artistName)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                if let albumName = track.albumName, !albumName.isEmpty {
                    Text(albumName)
                        .font(.footnote)
                        .foregroundStyle(.tertiary)
                        .lineLimit(1)
                }
                Text(providerDisplayName)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.secondary)
            }

            Spacer(minLength: 8)

            Image(systemName: "chevron.right")
                .font(.footnote.weight(.semibold))
                .foregroundStyle(.tertiary)
        }
        .contentShape(Rectangle())
    }

    @ViewBuilder
    private var artwork: some View {
        if let artworkUrl = track.artworkUrl, let url = URL(string: artworkUrl) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    ProgressView()
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFill()
                case .failure:
                    placeholderArtwork
                @unknown default:
                    placeholderArtwork
                }
            }
            .frame(width: 58, height: 58)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 8))
        } else {
            placeholderArtwork
        }
    }

    private var placeholderArtwork: some View {
        Image(systemName: "music.note")
            .font(.title3.weight(.semibold))
            .foregroundStyle(.secondary)
            .frame(width: 58, height: 58)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
    }

    private var providerDisplayName: String {
        switch track.provider {
        case "apple_music":
            return "Apple Music"
        case "spotify":
            return "Spotify"
        default:
            return track.provider
        }
    }
}

#Preview("Track Search Result") {
    TrackSearchResultRow(track: .previewSpotify)
        .padding()
}
