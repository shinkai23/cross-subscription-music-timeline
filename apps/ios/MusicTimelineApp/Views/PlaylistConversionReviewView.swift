import SwiftUI

struct PlaylistConversionReviewView: View {
    let items: [PlaylistConversionItem]

    var body: some View {
        List {
            Section {
                ForEach(items) { item in
                    HStack(alignment: .top, spacing: 12) {
                        Text("\(item.position)")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                            .frame(width: 28, alignment: .trailing)

                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.sourceTitle)
                                .font(.headline)

                            Text(item.sourceArtist)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)

                            if let matchedTitle = item.matchedTitle, let matchedArtist = item.matchedArtist {
                                Text("Matched: \(matchedTitle) - \(matchedArtist)")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }

                        Spacer()

                        statusIcon(for: item.state)
                    }
                    .padding(.vertical, 6)
                }
            } header: {
                Text("Review matches before creating the playlist")
            }

            Section {
                Button {
                    // TODO: Call backend conversion endpoint, then Apple Music playlist creation.
                } label: {
                    Label("Create Apple Music Playlist", systemImage: "plus.rectangle.on.rectangle")
                }
            }
        }
        .navigationTitle("Convert Playlist")
    }

    private func statusIcon(for state: PlaylistConversionItem.State) -> some View {
        switch state {
        case .matched:
            return Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
        case .needsReview:
            return Image(systemName: "exclamationmark.circle.fill").foregroundStyle(.orange)
        case .unavailable:
            return Image(systemName: "xmark.circle.fill").foregroundStyle(.red)
        }
    }
}

#Preview {
    PlaylistConversionReviewView(items: MockTimelineService.conversionItems)
}

