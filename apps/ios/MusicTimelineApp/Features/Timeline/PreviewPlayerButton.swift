//
//  PreviewPlayerButton.swift
//  MusicTimelineApp
//

import AVFoundation
import SwiftUI

struct PreviewPlayerButton: View {
    let previewUrl: String?

    @State private var player: AVPlayer?
    @State private var isPlaying = false

    private var url: URL? {
        guard let previewUrl else { return nil }
        return URL(string: previewUrl)
    }

    var body: some View {
        Button {
            togglePlayback()
        } label: {
            Label(isPlaying ? "Stop" : "Preview", systemImage: isPlaying ? "stop.fill" : "play.fill")
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
        .disabled(url == nil)
        .onDisappear {
            stopPlayback()
        }
    }

    private func togglePlayback() {
        guard let url else { return }

        if isPlaying {
            stopPlayback()
            return
        }

        let player = AVPlayer(url: url)
        self.player = player
        player.play()
        isPlaying = true
    }

    private func stopPlayback() {
        player?.pause()
        player = nil
        isPlaying = false
    }
}

#Preview("Preview Button") {
    PreviewPlayerButton(previewUrl: "https://example.com/preview.mp3")
        .padding()
}
