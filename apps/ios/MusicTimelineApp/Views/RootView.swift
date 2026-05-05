import SwiftUI

struct RootView: View {
    @State private var selectedProvider: MusicProvider? = MockTimelineService.currentUser.primaryProvider

    var body: some View {
        TabView {
            TimelineView(
                posts: MockTimelineService.posts,
                selectedProvider: selectedProvider ?? .appleMusic
            )
            .tabItem {
                Label("Timeline", systemImage: "music.note.list")
            }

            ServiceSelectionView(selectedProvider: $selectedProvider)
                .tabItem {
                    Label("Services", systemImage: "link")
                }

            PostComposerView()
                .tabItem {
                    Label("Post", systemImage: "plus.circle")
                }
        }
    }
}

#Preview {
    RootView()
}

