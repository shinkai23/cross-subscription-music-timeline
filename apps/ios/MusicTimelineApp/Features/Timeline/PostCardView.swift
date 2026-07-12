//
//  PostCardView.swift
//  MusicTimelineApp
//

import SwiftUI

struct PostCardView: View {
    let post: PostDTO

    private var playback: PlaybackDTO {
        post.playback
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                artwork

                VStack(alignment: .leading, spacing: 5) {
                    Text(playback.title)
                        .font(.headline)
                        .lineLimit(2)
                    Text(playback.artistName)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                    if let albumName = playback.albumName, !albumName.isEmpty {
                        Text(albumName)
                            .font(.footnote)
                            .foregroundStyle(.tertiary)
                            .lineLimit(1)
                    }
                    providerBadge
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            if let caption = post.caption, !caption.isEmpty {
                Text(caption)
                    .font(.subheadline)
                    .fixedSize(horizontal: false, vertical: true)
            }

            HStack(spacing: 10) {
                if playback.previewUrl != nil {
                    PreviewPlayerButton(previewUrl: playback.previewUrl)
                }
                OpenInProviderButton(
                    providerName: providerDisplayName,
                    providerUrl: playback.providerUrl
                )
            }
        }
        .padding(14)
        .background(.background, in: RoundedRectangle(cornerRadius: 8))
        .overlay {
            RoundedRectangle(cornerRadius: 8)
                .stroke(.quaternary, lineWidth: 1)
        }
    }

    @ViewBuilder
    private var artwork: some View {
        if let artworkUrl = playback.artworkUrl, let url = URL(string: artworkUrl) {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    ProgressView()
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFill()
                case .failure:
                    Image(systemName: "music.note")
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(.secondary)
                @unknown default:
                    EmptyView()
                }
            }
            .frame(width: 82, height: 82)
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 8))
        } else {
            Image(systemName: "music.note")
                .font(.title2.weight(.semibold))
                .foregroundStyle(.secondary)
                .frame(width: 82, height: 82)
                .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
        }
    }

    private var providerBadge: some View {
        Text(providerDisplayName)
            .font(.caption.weight(.bold))
            .foregroundStyle(.secondary)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(.thinMaterial, in: Capsule())
    }

    private var providerDisplayName: String {
        switch playback.provider {
        case "apple_music":
            return "Apple Music"
        case "spotify":
            return "Spotify"
        default:
            return playback.provider
        }
    }
}

#Preview("Post Card") {
    VStack(spacing: 14) {
        PostCardView(post: .spotifyPreview)
        PostCardView(post: .appleMusicExternal)
    }
    .padding()
}
