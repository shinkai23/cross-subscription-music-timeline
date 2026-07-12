//
//  CreatePostView.swift
//  MusicTimelineApp
//

import SwiftUI

struct CreatePostView: View {
    let track: TrackSearchResultDTO
    var apiClient: APIClient = .shared
    let onPostCreated: (PostDTO) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var playback: PlaybackDTO?
    @State private var caption = ""
    @State private var isLoadingPlayback = false
    @State private var isPosting = false
    @State private var errorMessage: String?
    @State private var providerConnectionRequired: String?
    @State private var isShowingSpotifyConnect = false

    var body: some View {
        Form {
            Section("Track") {
                TrackSearchResultRow(track: track)

                if isLoadingPlayback {
                    HStack {
                        ProgressView()
                        Text("Preparing playback metadata...")
                            .foregroundStyle(.secondary)
                    }
                }

                if let playback {
                    playbackSummary(playback)
                }
            }

            if let providerConnectionRequired {
                Section {
                    ProviderConnectionRequiredView(provider: providerConnectionRequired) {
                        isShowingSpotifyConnect = true
                    }
                }
            }

            Section("Caption") {
                TextField("Add a caption", text: $caption, axis: .vertical)
                    .lineLimit(3...6)
            }

            if let errorMessage {
                Section {
                    Text(errorMessage)
                        .font(.subheadline)
                        .foregroundStyle(.red)
                }
            }

            Section {
                Button {
                    Task {
                        await createPost()
                    }
                } label: {
                    if isPosting {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Post")
                            .frame(maxWidth: .infinity)
                    }
                }
                .disabled(isPosting || isLoadingPlayback || playback == nil)
            }
        }
        .navigationTitle("Create Post")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("Cancel") {
                    dismiss()
                }
            }
        }
        .task {
            await preparePlayback()
        }
        .sheet(isPresented: $isShowingSpotifyConnect) {
            SpotifyConnectView { response in
                UserDefaults.standard.set(
                    response.providerUserId,
                    forKey: "provider.spotify.providerUserId"
                )
                providerConnectionRequired = nil
                Task {
                    await preparePlayback(force: true)
                }
            }
        }
    }

    private func playbackSummary(_ playback: PlaybackDTO) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label(
                playback.playbackMode == "preview" ? "Preview available" : "Opens in provider",
                systemImage: playback.previewUrl == nil ? "arrow.up.forward.square" : "play.circle"
            )
            .font(.subheadline.weight(.semibold))

            if playback.previewUrl == nil {
                Text("This track will open in \(providerDisplayName).")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
    }

    @MainActor
    private func preparePlayback(force: Bool = false) async {
        if force {
            playback = nil
        }

        guard playback == nil, !isLoadingPlayback else { return }

        isLoadingPlayback = true
        errorMessage = nil
        providerConnectionRequired = nil

        if track.provider == "apple_music" {
            providerConnectionRequired = track.provider
            isLoadingPlayback = false
            return
        }

        do {
            playback = try await apiClient.fetchPlayback(
                provider: track.provider,
                trackId: track.providerTrackId
            )
        } catch {
            if let apiError = error as? APIClientError,
               apiError.isProviderConnectionRequired {
                providerConnectionRequired = track.provider
            } else {
                errorMessage = error.localizedDescription
            }
        }

        isLoadingPlayback = false
    }

    @MainActor
    private func createPost() async {
        guard let playback, !isPosting else { return }

        isPosting = true
        errorMessage = nil
        providerConnectionRequired = nil

        do {
            let post = try await apiClient.createPost(
                provider: playback.provider,
                providerTrackId: playback.providerTrackId,
                caption: trimmedCaption.isEmpty ? nil : trimmedCaption,
                visibility: "public"
            )
            onPostCreated(post)
        } catch {
            if let apiError = error as? APIClientError,
               apiError.isProviderConnectionRequired {
                providerConnectionRequired = playback.provider
            } else {
                errorMessage = error.localizedDescription
            }
        }

        isPosting = false
    }

    private var trimmedCaption: String {
        caption.trimmingCharacters(in: .whitespacesAndNewlines)
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

#Preview("Create Post") {
    NavigationStack {
        CreatePostView(track: .previewSpotify) { _ in }
    }
}
