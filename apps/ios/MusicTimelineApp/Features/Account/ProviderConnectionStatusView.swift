//
//  ProviderConnectionStatusView.swift
//  MusicTimelineApp
//

import SwiftUI

struct ProviderConnectionStatusView: View {
    let providerName: String
    let isConnected: Bool
    let providerUserId: String?

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: isConnected ? "checkmark.circle.fill" : "circle")
                .font(.title3)
                .foregroundStyle(isConnected ? .green : .secondary)

            VStack(alignment: .leading, spacing: 3) {
                Text(providerName)
                    .font(.headline.weight(.semibold))
                Text(statusText)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
            }

            Spacer()
        }
        .padding(14)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
    }

    private var statusText: String {
        guard isConnected else {
            return "Not connected"
        }

        if let providerUserId, !providerUserId.isEmpty {
            return "Connected as \(providerUserId)"
        }

        return "Spotify connected"
    }
}

#Preview("Provider Status") {
    VStack {
        ProviderConnectionStatusView(
            providerName: "Spotify",
            isConnected: true,
            providerUserId: "spotify-user-1"
        )
        ProviderConnectionStatusView(
            providerName: "Spotify",
            isConnected: false,
            providerUserId: nil
        )
    }
    .padding()
}
