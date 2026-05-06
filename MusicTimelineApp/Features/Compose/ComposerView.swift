//
//  ComposerView.swift
//  MusicTimelineApp
//

import SwiftUI

struct ComposerView: View {
    let signedInName: String
    let theme: Theme
    let copy: Copybook
    let onSubmit: (PostDraft) -> Void
    @Environment(\.dismiss) private var dismiss
    @State private var draft = PostDraft()

    private let suggestedTags = ["night-drive", "alt-pop", "rock", "focus", "new-drop", "repeat"]
    private let suggestedMoments = ["commute", "2am", "first listen", "gym reset", "rainy walk", "group chat"]

    private var trimmedTitle: String {
        draft.title.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var trimmedArtist: String {
        draft.artistName.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var canPublish: Bool {
        !trimmedTitle.isEmpty && !trimmedArtist.isEmpty
    }

    private var libraryAssets: [SubscriptionLibraryAsset] {
        SubscriptionLibraryAsset.assets(for: draft.serviceName)
    }

    private var selectedAsset: SubscriptionLibraryAsset? {
        libraryAssets.first { $0.id == draft.sourceLibraryID }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    previewCard

                    formCard(title: copy.sourceLibraryTitle, subtitle: copy.sourceLibrarySubtitle) {
                        VStack(alignment: .leading, spacing: 14) {
                            Picker(copy.providerTitle, selection: $draft.serviceName) {
                                Text("Spotify").tag("Spotify")
                                Text("Apple Music").tag("Apple Music")
                                Text("YouTube Music").tag("YouTube Music")
                            }
                            .pickerStyle(.segmented)
                            .onChange(of: draft.serviceName) { _, _ in
                                syncSourceSelection()
                            }

                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 14) {
                                    ForEach(libraryAssets) { asset in
                                        libraryAssetCard(asset)
                                    }
                                }
                            }
                        }
                    }

                    formCard {
                        VStack(alignment: .leading, spacing: 14) {
                            LabeledContent(copy.displayNameTitle, value: signedInName.isEmpty ? "musicfan" : signedInName)
                                .foregroundStyle(theme.primaryText)

                            textField("Title", text: $draft.title)
                            textField("Artist", text: $draft.artistName)
                            textField("Context", text: $draft.metadataLine)
                            textField("Caption", text: $draft.caption, axis: .vertical)
                            textField(copy.hookPlaceholder, text: $draft.shareHook, axis: .vertical)
                            textField("Tags: rock, drive", text: $draft.tagsText)
                        }
                    }

                    formCard(title: copy.quickTagsTitle) {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 10) {
                                ForEach(suggestedTags, id: \.self) { tag in
                                    Button {
                                        appendTag(tag)
                                    } label: {
                                        Text("#\(tag)")
                                            .font(.caption.weight(.bold))
                                            .foregroundStyle(theme.primaryText)
                                            .padding(.horizontal, 12)
                                            .padding(.vertical, 10)
                                            .background(theme.chromeStrong, in: Capsule())
                                            .overlay {
                                                Capsule()
                                                    .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.2)
                                            }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }

                    formCard(title: copy.postMomentsTitle) {
                        FlowLayout(data: suggestedMoments, spacing: 10) { moment in
                            Button {
                                toggleMoment(moment)
                            } label: {
                                Text(moment)
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(draft.selectedMoments.contains(moment) ? theme.background : theme.primaryText)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 10)
                                    .background(
                                        draft.selectedMoments.contains(moment) ? theme.primaryText : theme.chromeStrong,
                                        in: Capsule()
                                    )
                            }
                            .buttonStyle(.plain)
                        }
                    }

                    formCard(title: copy.appearance) {
                        VStack(spacing: 12) {
                            Picker(copy.postTypeLabel(.track), selection: $draft.postType) {
                                Text(copy.postTypeLabel(.track)).tag(MusicPostType.track)
                                Text(copy.postTypeLabel(.album)).tag(MusicPostType.album)
                                Text(copy.postTypeLabel(.playlist)).tag(MusicPostType.playlist)
                            }
                            .pickerStyle(.segmented)

                            Toggle(copy.newLabel, isOn: $draft.isNewRelease)
                                .tint(theme.toolbarTint)
                        }
                    }

                    if !canPublish {
                        Text(copy.requiredFieldHint)
                            .font(.footnote.weight(.semibold))
                            .foregroundStyle(theme.secondaryText)
                            .padding(.horizontal, 4)
                    }
                }
                .padding(16)
                .padding(.bottom, 24)
            }
            .background(theme.background)
            .navigationTitle(copy.composeShort)
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                syncSourceSelection()
            }
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button(copy.done) { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button(copy.publishPostTitle) {
                        onSubmit(draft)
                        dismiss()
                    }
                    .disabled(!canPublish)
                }
            }
        }
        .preferredColorScheme(theme.isDark ? .dark : .light)
    }

    private var previewCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(copy.previewCardTitle)
                .font(.headline.weight(.bold))
                .foregroundStyle(theme.primaryText)

            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [serviceColor.opacity(0.95), theme.cardRaised, .black],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .aspectRatio(1, contentMode: .fit)
                .overlay(alignment: .topTrailing) {
                    Text(copy.postTypeEnglishLabel(draft.postType))
                        .font(.caption2.weight(.black))
                        .tracking(1.4)
                        .foregroundStyle(theme.background)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(theme.primaryText, in: Capsule())
                        .padding(16)
                }
                .overlay(alignment: .bottomLeading) {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(trimmedTitle.isEmpty ? "Untitled Post" : trimmedTitle)
                            .font(.system(size: 30, weight: .black, design: .rounded))
                            .foregroundStyle(.white)
                            .lineLimit(2)
                        Text(trimmedArtist.isEmpty ? "Unknown Artist" : trimmedArtist)
                            .font(.headline.weight(.semibold))
                            .foregroundStyle(.white.opacity(0.82))
                        Text(draft.metadataLine.isEmpty ? "Set the context for this post." : draft.metadataLine)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.white.opacity(0.72))
                        if let selectedAsset {
                            Text(selectedAsset.momentumLabel)
                                .font(.caption2.weight(.black))
                                .tracking(1.2)
                                .foregroundStyle(.white)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(.black.opacity(0.22), in: Capsule())
                        }
                    }
                    .padding(18)
                }
        }
    }

    private var serviceColor: Color {
        switch draft.serviceName {
        case "Spotify":
            return theme.spotify
        case "Apple Music":
            return theme.appleMusic
        case "YouTube Music":
            return theme.youTubeMusic
        default:
            return theme.serviceDefault
        }
    }

    private func formCard<Content: View>(
        title: String? = nil,
        subtitle: String? = nil,
        @ViewBuilder content: () -> Content
    ) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            if let title {
                Text(title)
                    .font(.headline.weight(.bold))
                    .foregroundStyle(theme.primaryText)
            }
            if let subtitle {
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(theme.secondaryText)
            }
            content()
        }
        .padding(18)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 26, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }

    private func textField(_ title: String, text: Binding<String>, axis: Axis = .horizontal) -> some View {
        TextField(title, text: text, axis: axis)
            .foregroundStyle(theme.primaryText)
            .padding(.horizontal, 14)
            .padding(.vertical, axis == .horizontal ? 12 : 14)
            .background(theme.cardRaised, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.2)
            }
    }

    private func appendTag(_ tag: String) {
        let existing = draft.tags
        guard !existing.contains(tag) else { return }
        if draft.tagsText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            draft.tagsText = tag
        } else {
            draft.tagsText += ", \(tag)"
        }
    }

    private func toggleMoment(_ moment: String) {
        if draft.selectedMoments.contains(moment) {
            draft.selectedMoments.removeAll { $0 == moment }
        } else {
            draft.selectedMoments.append(moment)
        }
    }

    private func syncSourceSelection() {
        if let selectedAsset, selectedAsset.serviceName == draft.serviceName {
            return
        }

        if let firstAsset = libraryAssets.first {
            applyAsset(firstAsset)
        }
    }

    private func applyAsset(_ asset: SubscriptionLibraryAsset) {
        draft.sourceLibraryID = asset.id
        draft.serviceName = asset.serviceName
        draft.postType = asset.postType
        draft.title = asset.title
        draft.artistName = asset.creatorName
        draft.metadataLine = asset.metadataLine
        draft.caption = asset.captionSeed
        draft.tagsText = asset.tags.joined(separator: ", ")
        draft.shareHook = asset.momentumLabel
    }

    private func libraryAssetCard(_ asset: SubscriptionLibraryAsset) -> some View {
        let isSelected = draft.sourceLibraryID == asset.id

        return Button {
            applyAsset(asset)
        } label: {
            VStack(alignment: .leading, spacing: 10) {
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [serviceColor(for: asset), theme.cardRaised, .black],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 178, height: 178)
                    .overlay(alignment: .bottomLeading) {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(asset.title)
                                .font(.headline.weight(.black))
                                .foregroundStyle(.white)
                                .lineLimit(2)
                            Text(asset.creatorName)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(.white.opacity(0.82))
                                .lineLimit(1)
                            Text(asset.momentumLabel)
                                .font(.caption2.weight(.bold))
                                .foregroundStyle(.white.opacity(0.78))
                        }
                        .padding(14)
                    }

                Text(asset.metadataLine)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(theme.secondaryText)
                    .lineLimit(2)
            }
            .frame(width: 178, alignment: .leading)
            .padding(8)
            .background(isSelected ? theme.chromeStrong : Color.clear, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .stroke(isSelected ? theme.primaryText.opacity(0.35) : theme.line, lineWidth: isSelected ? 1.2 : 1)
            }
        }
        .buttonStyle(.plain)
    }

    private func serviceColor(for asset: SubscriptionLibraryAsset) -> Color {
        switch asset.serviceName {
        case "Spotify":
            return theme.spotify
        case "Apple Music":
            return theme.appleMusic
        case "YouTube Music":
            return theme.youTubeMusic
        default:
            return theme.serviceDefault
        }
    }
}

#Preview {
    ComposerView(
        signedInName: "sinkaii",
        theme: .dark,
        copy: Copybook(language: .english)
    ) { _ in }
}
