import SwiftUI

struct TimelineView: View {
    let posts: [MusicPost]
    let selectedProvider: MusicProvider

    var body: some View {
        NavigationStack {
            List(posts) { post in
                NavigationLink {
                    if post.itemType == .playlist {
                        PlaylistConversionReviewView(items: MockTimelineService.conversionItems)
                    } else {
                        MusicPostDetailView(post: post, selectedProvider: selectedProvider)
                    }
                } label: {
                    MusicPostRow(post: post, selectedProvider: selectedProvider)
                }
                .listRowSeparator(.hidden)
            }
            .listStyle(.plain)
            .navigationTitle("Timeline")
        }
    }
}

private struct MusicPostRow: View {
    let post: MusicPost
    let selectedProvider: MusicProvider

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .top, spacing: 12) {
                RoundedRectangle(cornerRadius: 8)
                    .fill(.quaternary)
                    .frame(width: 72, height: 72)
                    .overlay {
                        Image(systemName: post.itemType == .playlist ? "music.note.list" : "music.note")
                            .foregroundStyle(.secondary)
                    }

                VStack(alignment: .leading, spacing: 4) {
                    Text(post.title)
                        .font(.headline)

                    Text(post.subtitle)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)

                    Text("@\(post.author.handle) via \(post.sourceProvider.displayName)")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Text(post.caption)
                .font(.body)

            if !post.tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack {
                        ForEach(post.tags, id: \.self) { tag in
                            Text("#\(tag)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
            }

            HStack {
                if let matchSummary = post.matchSummary {
                    Label(matchSummary.displayText, systemImage: matchSummary.needsReviewCount > 0 ? "exclamationmark.circle" : "checkmark.circle")
                        .font(.caption)
                        .foregroundStyle(matchSummary.needsReviewCount > 0 ? .orange : .green)
                }

                Spacer()

                Label("Open in \(selectedProvider.displayName)", systemImage: "play.circle")
                    .font(.caption)
                    .foregroundStyle(.tint)
            }
        }
        .padding(.vertical, 8)
    }
}

private struct MusicPostDetailView: View {
    let post: MusicPost
    let selectedProvider: MusicProvider

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(post.title)
                .font(.title)
                .bold()

            Text(post.subtitle)
                .foregroundStyle(.secondary)

            Text(post.caption)

            Button {
                // TODO: Open provider URL or resolved target-provider URL.
            } label: {
                Label("Open in \(selectedProvider.displayName)", systemImage: "play.circle.fill")
            }
            .buttonStyle(.borderedProminent)

            Spacer()
        }
        .padding()
        .navigationTitle("Post")
    }
}

#Preview {
    TimelineView(posts: MockTimelineService.posts, selectedProvider: .appleMusic)
}

