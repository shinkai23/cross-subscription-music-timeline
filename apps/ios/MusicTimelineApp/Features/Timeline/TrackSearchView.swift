//
//  TrackSearchView.swift
//  MusicTimelineApp
//

import SwiftUI

struct TrackSearchView: View {
    var apiClient: APIClient = .shared
    let onPostCreated: (PostDTO) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var provider: SearchProvider = .spotify
    @State private var query = ""
    @State private var results: [TrackSearchResultDTO] = []
    @State private var selectedTrack: TrackSearchResultDTO?
    @State private var isSearching = false
    @State private var hasSearched = false
    @State private var errorMessage: String?
    @State private var providerConnectionRequired: String?
    @State private var isShowingSpotifyConnect = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                searchControls

                content
            }
            .navigationTitle("Search Track")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                }
            }
            .navigationDestination(item: $selectedTrack) { track in
                CreatePostView(track: track, apiClient: apiClient) { post in
                    onPostCreated(post)
                    dismiss()
                }
            }
        }
        .sheet(isPresented: $isShowingSpotifyConnect) {
            SpotifyConnectView { response in
                UserDefaults.standard.set(
                    response.providerUserId,
                    forKey: "provider.spotify.providerUserId"
                )
                providerConnectionRequired = nil
                Task {
                    await search()
                }
            }
        }
    }

    private var searchControls: some View {
        VStack(spacing: 12) {
            Picker("Provider", selection: $provider) {
                ForEach(SearchProvider.allCases) { provider in
                    Text(provider.displayName).tag(provider)
                }
            }
            .pickerStyle(.segmented)

            HStack(spacing: 10) {
                TextField("Song or artist", text: $query)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .textFieldStyle(.roundedBorder)
                    .submitLabel(.search)
                    .onSubmit {
                        Task {
                            await search()
                        }
                    }

                Button {
                    Task {
                        await search()
                    }
                } label: {
                    Image(systemName: "magnifyingglass")
                        .frame(width: 34, height: 34)
                }
                .buttonStyle(.borderedProminent)
                .disabled(trimmedQuery.isEmpty || isSearching)
            }
        }
        .padding()
        .background(.background)
    }

    @ViewBuilder
    private var content: some View {
        if isSearching {
            ProgressView()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let providerConnectionRequired {
            ProviderConnectionRequiredView(provider: providerConnectionRequired) {
                isShowingSpotifyConnect = true
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else if let errorMessage {
            messageState(
                title: "Search failed",
                message: errorMessage,
                systemImage: "exclamationmark.triangle"
            )
        } else if results.isEmpty && hasSearched {
            messageState(
                title: "No tracks found",
                message: "Try a different song title or artist name.",
                systemImage: "music.note.list"
            )
        } else if results.isEmpty {
            messageState(
                title: "Find a track",
                message: "Search Spotify or Apple Music, then choose a track to post.",
                systemImage: "magnifyingglass"
            )
        } else {
            List(results) { track in
                Button {
                    selectedTrack = track
                } label: {
                    TrackSearchResultRow(track: track)
                }
                .buttonStyle(.plain)
            }
            .listStyle(.plain)
        }
    }

    private func messageState(
        title: String,
        message: String,
        systemImage: String
    ) -> some View {
        VStack(spacing: 10) {
            Image(systemName: systemImage)
                .font(.title2)
                .foregroundStyle(.secondary)
            Text(title)
                .font(.headline)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    @MainActor
    private func search() async {
        guard !trimmedQuery.isEmpty, !isSearching else { return }

        isSearching = true
        hasSearched = true
        errorMessage = nil
        providerConnectionRequired = nil

        if provider == .appleMusic {
            results = []
            providerConnectionRequired = provider.rawValue
            isSearching = false
            return
        }

        do {
            results = try await apiClient.searchTracks(
                provider: provider.rawValue,
                query: trimmedQuery
            )
        } catch {
            results = []
            if let apiError = error as? APIClientError,
               apiError.isProviderConnectionRequired {
                providerConnectionRequired = provider.rawValue
            } else {
                errorMessage = error.localizedDescription
            }
        }

        isSearching = false
    }

    private var trimmedQuery: String {
        query.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

#Preview("Track Search") {
    TrackSearchView { _ in }
}
