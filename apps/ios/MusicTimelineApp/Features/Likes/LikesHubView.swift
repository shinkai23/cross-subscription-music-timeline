//
//  LikesHubView.swift
//  MusicTimelineApp
//

import SwiftUI

struct LikesHubView: View {
    let items: [Item]
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    let onMetricsChange: (CGFloat) -> Void

    @State private var selectedSection: LikesSection = .liked
    @State private var previousOffset: CGFloat = 0

    private var likedItems: [Item] { items.filter(\.isLikedByUser) }
    private var savedItems: [Item] { items.filter(\.isSavedByUser) }
    private var activityItems: [ActivityNotification] {
        items
            .filter(\.isOwnedByCurrentUser)
            .sorted { $0.playedAt > $1.playedAt }
            .map {
                ActivityNotification(
                    title: "\($0.title)",
                    body: "\($0.likeCount) likes, \($0.commentCount) comments, \($0.repostCount) reposts, \($0.saveCount) saves",
                    symbolName: "bell.badge.fill",
                    timestamp: $0.playedAt.formatted(date: .omitted, time: .shortened)
                )
            }
    }

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 20, pinnedViews: [.sectionHeaders]) {
                GeometryReader { proxy in
                    Color.clear
                        .preference(key: FeedOffsetPreferenceKey.self, value: proxy.frame(in: .named("likesScroll")).minY)
                }
                .frame(height: 0)

                Section {
                    VStack(alignment: .leading, spacing: 20) {
                        headerIntro
                        snapshotRow
                        content
                    }
                } header: {
                    LikesSectionStrip(selectedSection: $selectedSection, theme: theme, copy: copy)
                        .padding(.vertical, 8)
                        .background(theme.background)
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 96)
        }
        .coordinateSpace(name: "likesScroll")
        .onPreferenceChange(FeedOffsetPreferenceKey.self) { value in
            let delta = value - previousOffset
            let direction: ScrollDirection = delta < -1 ? .down : .up
            previousOffset = value
            let progress = direction == .down ? min(max((-value - 24) / 90, 0), 1) : 0
            onMetricsChange(progress)
        }
    }

    private var headerIntro: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(copy.likesTitle)
                .font(.system(size: 28, weight: .black, design: titleDesign))
                .foregroundStyle(theme.primaryText)
            Text("Liked songs, saved finds, and fresh reactions to your posts.")
                .font(.subheadline)
                .foregroundStyle(theme.secondaryText)
        }
    }

    private var snapshotRow: some View {
        HStack(spacing: 12) {
            statCard(value: likedItems.count.formatted(), title: copy.likedSectionTitle)
            statCard(value: savedItems.count.formatted(), title: copy.savedSectionTitle)
            statCard(value: activityItems.count.formatted(), title: copy.activitySectionTitle)
        }
    }

    @ViewBuilder
    private var content: some View {
        switch selectedSection {
        case .liked:
            LibraryShelf(
                title: copy.likedHighlightsTitle,
                subtitle: copy.likedHighlightsSubtitle,
                items: likedItems,
                theme: theme,
                copy: copy,
                titleDesign: titleDesign
            )
        case .saved:
            LibraryShelf(
                title: copy.savedHighlightsTitle,
                subtitle: copy.savedHighlightsSubtitle,
                items: savedItems,
                theme: theme,
                copy: copy,
                titleDesign: titleDesign
            )
        case .activity:
            ActivityFeed(notifications: activityItems, theme: theme, copy: copy)
        }
    }

    private func statCard(value: String, title: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(value)
                .font(.system(size: 24, weight: .black, design: titleDesign))
                .foregroundStyle(theme.primaryText)
            Text(title)
                .font(.caption.weight(.bold))
                .foregroundStyle(theme.secondaryText)
                .lineLimit(2)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.4)
        }
    }
}

private struct LikesSectionStrip: View {
    @Binding var selectedSection: LikesSection
    let theme: Theme
    let copy: Copybook

    var body: some View {
        HStack(spacing: 8) {
            ForEach(LikesSection.allCases) { section in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedSection = section
                    }
                } label: {
                    Text(copy.likesSectionTitle(section))
                        .font(.subheadline.weight(selectedSection == section ? .bold : .semibold))
                        .foregroundStyle(selectedSection == section ? theme.primaryText : theme.secondaryText)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(
                            RoundedRectangle(cornerRadius: 14, style: .continuous)
                                .fill(selectedSection == section ? theme.chromeStrong : theme.chrome)
                        )
                }
                .buttonStyle(.plain)
            }
        }
    }
}

private struct LibraryShelf: View {
    let title: String
    let subtitle: String
    let items: [Item]
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.headline.weight(.bold))
                    .foregroundStyle(theme.primaryText)
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(theme.secondaryText)
            }

            if items.isEmpty {
                Text(copy.likesEmptyDescription)
                    .font(.subheadline)
                    .foregroundStyle(theme.secondaryText)
            } else {
                rewindShelf

                ForEach(items) { item in
                    TimelineCard(item: item, theme: theme, copy: copy, titleDesign: titleDesign)
                }
            }
        }
    }

    private var rewindShelf: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(alignment: .top, spacing: 14) {
                ForEach(Array(items.prefix(6))) { item in
                    VStack(alignment: .leading, spacing: 10) {
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .fill(
                                LinearGradient(
                                    colors: [theme.cardRaised, theme.card, accent(for: item)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                            .frame(width: 220, height: 220)
                            .overlay(alignment: .bottomLeading) {
                                VStack(alignment: .leading, spacing: 6) {
                                    Text(item.title)
                                        .font(.title3.weight(.black))
                                        .foregroundStyle(.white)
                                        .lineLimit(2)
                                    Text(item.creatorName)
                                        .font(.subheadline.weight(.semibold))
                                        .foregroundStyle(.white.opacity(0.82))
                                        .lineLimit(1)
                                }
                                .padding(16)
                            }

                        HStack(spacing: 8) {
                            metricChip(systemImage: "heart.fill", value: item.likeCount.formatted(.number.notation(.compactName)))
                            metricChip(systemImage: "bookmark.fill", value: item.saveCount.formatted(.number.notation(.compactName)))
                        }
                    }
                    .frame(width: 220, alignment: .leading)
                }
            }
        }
    }

    private func accent(for item: Item) -> Color {
        switch item.serviceName {
        case "Spotify": return theme.spotify
        case "Apple Music": return theme.appleMusic
        case "YouTube Music": return theme.youTubeMusic
            default: return theme.serviceDefault
        }
    }

    private func metricChip(systemImage: String, value: String) -> some View {
        HStack(spacing: 6) {
            Image(systemName: systemImage)
                .font(.caption.weight(.bold))
            Text(value)
                .font(.caption.weight(.bold))
        }
        .foregroundStyle(theme.primaryText)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(theme.chromeStrong, in: Capsule())
    }
}

private struct ActivityFeed: View {
    let notifications: [ActivityNotification]
    let theme: Theme
    let copy: Copybook

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if notifications.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text(copy.activityEmptyTitle)
                        .font(.headline.weight(.bold))
                        .foregroundStyle(theme.primaryText)
                    Text(copy.activityEmptySubtitle)
                        .font(.subheadline)
                        .foregroundStyle(theme.secondaryText)
                }
                .padding(18)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            } else {
                ForEach(notifications) { notification in
                    HStack(alignment: .top, spacing: 12) {
                        Image(systemName: notification.symbolName)
                            .font(.headline)
                            .foregroundStyle(theme.primaryText)
                            .frame(width: 34, height: 34)
                            .background(theme.chromeStrong, in: Circle())

                        VStack(alignment: .leading, spacing: 4) {
                            Text(notification.title)
                                .font(.headline.weight(.bold))
                                .foregroundStyle(theme.primaryText)
                            Text(notification.body)
                                .font(.subheadline)
                                .foregroundStyle(theme.secondaryText)
                            Text(notification.timestamp)
                                .font(.caption.weight(.bold))
                                .foregroundStyle(theme.tertiaryText)
                        }
                    }
                    .padding(16)
                    .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                    .overlay {
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
                    }
                }
            }
        }
    }
}
