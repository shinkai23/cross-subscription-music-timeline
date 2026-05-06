import SwiftUI

struct PostComposerView: View {
    @State private var query = ""
    @State private var caption = ""
    @State private var selectedType: MusicItemType = .song
    @State private var results: [MusicSearchResult] = []
    @State private var selectedResult: MusicSearchResult?
    @State private var isSearching = false
    @State private var errorMessage: String?

    private let appleMusicCatalogService = AppleMusicCatalogService()

    var body: some View {
        NavigationStack {
            Form {
                Section("Music") {
                    Picker("Type", selection: $selectedType) {
                        Text("Song").tag(MusicItemType.song)
                        Text("Album").tag(MusicItemType.album)
                        Text("Playlist").tag(MusicItemType.playlist)
                    }

                    TextField("Search Apple Music or Spotify", text: $query)

                    Button {
                        Task {
                            await search()
                        }
                    } label: {
                        if isSearching {
                            ProgressView()
                        } else {
                            Label("Search Apple Music", systemImage: "magnifyingglass")
                        }
                    }
                    .disabled(query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isSearching)

                    if let errorMessage {
                        Text(errorMessage)
                            .font(.caption)
                            .foregroundStyle(.red)
                    }
                }

                if !results.isEmpty {
                    Section("Results") {
                        ForEach(results) { result in
                            Button {
                                selectedResult = result
                                selectedType = result.itemType
                            } label: {
                                HStack {
                                    MusicSearchResultRow(result: result)

                                    Spacer()

                                    if selectedResult?.id == result.id {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(.tint)
                                    }
                                }
                            }
                        }
                    }
                }

                Section("Recommendation") {
                    TextEditor(text: $caption)
                        .frame(minHeight: 160)

                    Button {
                        // TODO: Request text-only AI draft from backend.
                    } label: {
                        Label("Draft caption", systemImage: "sparkles")
                    }
                }

                Section {
                    Button {
                        // TODO: Create post through backend.
                    } label: {
                        Label("Post", systemImage: "paperplane.fill")
                    }
                }
            }
            .navigationTitle("New Post")
        }
    }

    private func search() async {
        isSearching = true
        errorMessage = nil

        do {
            results = try await appleMusicCatalogService.search(term: query)
        } catch {
            errorMessage = "Apple Music search failed. Check authorization and network access."
        }

        isSearching = false
    }
}

#Preview {
    PostComposerView()
}
