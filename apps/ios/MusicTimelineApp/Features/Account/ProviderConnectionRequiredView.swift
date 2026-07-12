//
//  ProviderConnectionRequiredView.swift
//  MusicTimelineApp
//

import SwiftUI

struct ProviderConnectionRequiredView: View {
    let provider: String
    let onConnectSpotify: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: iconName)
                .font(.title2)
                .foregroundStyle(.secondary)

            Text(title)
                .font(.headline)
                .multilineTextAlignment(.center)

            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            if provider == "spotify" {
                Button {
                    onConnectSpotify()
                } label: {
                    Label("Connect Spotify", systemImage: "link")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .padding(.top, 4)
            }
        }
        .padding()
        .frame(maxWidth: .infinity)
    }

    private var iconName: String {
        provider == "spotify" ? "link.badge.plus" : "music.note"
    }

    private var title: String {
        switch provider {
        case "spotify":
            return "Spotify is not connected"
        case "apple_music":
            return "Apple Music connection is not available"
        default:
            return "Provider is not connected"
        }
    }

    private var message: String {
        switch provider {
        case "spotify":
            return "To search and post Spotify tracks, connect your Spotify account first."
        case "apple_music":
            return "Apple Music connection is not available in the current MVP. For now, use Spotify or open Apple Music tracks externally."
        default:
            return "Connect this provider before searching or posting tracks."
        }
    }
}

#Preview("Provider Required") {
    ProviderConnectionRequiredView(provider: "spotify") {}
        .padding()
}
