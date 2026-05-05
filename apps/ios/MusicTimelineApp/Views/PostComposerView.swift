import SwiftUI

struct PostComposerView: View {
    @State private var query = ""
    @State private var caption = ""
    @State private var selectedType: MusicItemType = .song

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
}

#Preview {
    PostComposerView()
}

