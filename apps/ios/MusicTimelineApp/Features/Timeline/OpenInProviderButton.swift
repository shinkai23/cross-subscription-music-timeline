//
//  OpenInProviderButton.swift
//  MusicTimelineApp
//

import SwiftUI

#if canImport(UIKit)
import UIKit
#endif

struct OpenInProviderButton: View {
    let providerName: String
    let providerUrl: String?

    private var url: URL? {
        guard let providerUrl else { return nil }
        return URL(string: providerUrl)
    }

    var body: some View {
        Button {
            openProvider()
        } label: {
            Label("Open", systemImage: "arrow.up.forward.square")
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.borderedProminent)
        .disabled(url == nil)
        .accessibilityLabel("Open in \(providerName)")
    }

    private func openProvider() {
        guard let url else { return }

        #if canImport(UIKit)
        UIApplication.shared.open(url)
        #endif
    }
}

#Preview("Open Button") {
    OpenInProviderButton(
        providerName: "Spotify",
        providerUrl: "https://open.spotify.com/track/spotify-track-1"
    )
    .padding()
}
