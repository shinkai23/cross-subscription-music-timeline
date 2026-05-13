//
//  TimelineComponents.swift
//  MusicTimelineApp
//

import SwiftUI
import SwiftData

struct FeedTabStrip: View {
    @Binding var selectedTab: FeedTab
    let theme: Theme
    let copy: Copybook
    let collapseProgress: CGFloat
    let onSearchTap: () -> Void

    var body: some View {
        HStack(spacing: 8) {
            ForEach(FeedTab.allCases) { tab in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTab = tab
                    }
                } label: {
                    VStack(spacing: 6) {
                        Text(copy.tabTitle(tab))
                            .font(.system(size: 14, weight: selectedTab == tab ? .bold : .semibold))
                            .foregroundStyle(selectedTab == tab ? theme.primaryText : theme.secondaryText)
                            .lineLimit(1)
                        Capsule()
                            .fill(selectedTab == tab ? theme.primaryText : .clear)
                            .frame(height: 2.5)
                            .opacity(selectedTab == tab ? max(0.55, collapseProgress) : 0)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .contentShape(Rectangle())
                    .background {
                        if selectedTab == tab {
                            Capsule()
                                .fill(theme.primaryText.opacity(theme.isDark ? 0.05 : 0.07))
                        }
                    }
                }
                .buttonStyle(.plain)
            }

            Button(action: onSearchTap) {
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 15, weight: .bold))
                    .foregroundStyle(theme.primaryText)
                    .frame(width: 42, height: 40)
                    .overlay {
                        Circle()
                            .stroke(theme.line.opacity(0.4 + (collapseProgress * 0.35)), lineWidth: theme.isDark ? 0.8 : 1.1)
                    }
            }
            .buttonStyle(.plain)
        }
    }
}

struct FeaturedRail: View {
    let items: [Item]
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    var onSearchTermTap: ((String) -> Void)? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            VStack(alignment: .leading, spacing: 4) {
                Text(copy.featuredRailTitle)
                    .font(.system(size: 20, weight: .black, design: titleDesign))
                    .foregroundStyle(theme.primaryText)
                Text(copy.featuredRailSubtitle)
                    .font(.footnote.weight(.medium))
                    .foregroundStyle(theme.secondaryText)
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 14) {
                    ForEach(Array(items.prefix(4))) { item in
                        VStack(alignment: .leading, spacing: 10) {
                            Button {
                                onSearchTermTap?(item.title)
                            } label: {
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .fill(
                                        LinearGradient(
                                            colors: [theme.chromeStrong, theme.cardRaised, serviceColor(for: item)],
                                            startPoint: .topLeading,
                                            endPoint: .bottomTrailing
                                        )
                                    )
                                    .frame(width: 164, height: 164)
                                    .overlay(alignment: .bottomLeading) {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(item.title)
                                                .font(.headline.weight(.bold))
                                                .foregroundStyle(coverTextColor(for: serviceColor(for: item)))
                                                .lineLimit(2)
                                            Text(item.creatorName)
                                                .font(.caption.weight(.medium))
                                                .foregroundStyle(coverSecondaryTextColor(for: serviceColor(for: item)))
                                        }
                                        .padding(14)
                                    }
                            }
                            .buttonStyle(.plain)

                            Button {
                                onSearchTermTap?(item.serviceName)
                            } label: {
                                Text(item.serviceName)
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(theme.secondaryText)
                            }
                            .buttonStyle(.plain)
                            .frame(width: 164, alignment: .leading)
                        }
                        .frame(width: 164, alignment: .leading)
                    }
                }
            }
        }
        .padding(16)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }

    private func coverTextColor(for color: Color) -> Color {
        color.isPerceptuallyLight ? Color.black.opacity(0.88) : .white
    }

    private func coverSecondaryTextColor(for color: Color) -> Color {
        color.isPerceptuallyLight ? Color.black.opacity(0.62) : .white.opacity(0.82)
    }

    private func serviceColor(for item: Item) -> Color {
        switch item.serviceName {
        case "Spotify": return theme.spotify
        case "Apple Music": return theme.appleMusic
        case "YouTube Music": return theme.youTubeMusic
        default: return theme.serviceDefault
        }
    }
}

struct BottomTabBar: View {
    @Binding var selectedTab: RootTab
    let theme: Theme
    let copy: Copybook
    let hiddenProgress: CGFloat
    let onComposeTap: () -> Void

    var body: some View {
        HStack {
            ForEach(RootTab.allCases) { tab in
                Button {
                    if tab == .compose {
                        onComposeTap()
                    } else {
                        withAnimation(.spring(duration: 0.28)) {
                            selectedTab = tab
                        }
                    }
                } label: {
                    VStack(spacing: 6) {
                        Image(systemName: iconName(for: tab))
                            .font(.system(size: 18, weight: .semibold))
                        Text(copy.rootTitle(tab))
                            .font(.caption.weight(.bold))
                    }
                    .foregroundStyle(selectedTab == tab && tab != .compose ? theme.primaryText : theme.secondaryText)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(theme.card.opacity(theme.isDark ? 0.94 : 0.98), in: Capsule())
        .overlay {
            Capsule()
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
        .shadow(color: theme.shadow, radius: 18, x: 0, y: 8)
        .offset(y: hiddenProgress * 110)
        .opacity(1 - hiddenProgress)
    }

    private func iconName(for tab: RootTab) -> String {
        switch tab {
        case .home:
            return "house.fill"
        case .compose:
            return "plus.circle.fill"
        case .likes:
            return "heart.fill"
        case .account:
            return "person.crop.circle"
        }
    }
}

struct TimelineCard: View {
    @Bindable var item: Item
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    var onSearchTermTap: ((String) -> Void)? = nil
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            jacket

            Button {
                withAnimation(.easeInOut(duration: 0.22)) {
                    isExpanded.toggle()
                }
            } label: {
                HStack(spacing: 8) {
                    Text(isExpanded ? "Hide details" : "More")
                        .font(.caption.weight(.bold))
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.caption.weight(.bold))
                    Spacer()
                    Text(item.playedAt, format: .relative(presentation: .named))
                        .font(.caption.weight(.semibold))
                }
                .foregroundStyle(theme.secondaryText)
            }
            .buttonStyle(.plain)

            if isExpanded {
                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 8) {
                        searchLabel(item.serviceName, tint: serviceColor)
                        searchLabel(copy.postTypeLabel(item.postType), tint: theme.primaryText.opacity(0.75), query: item.postType.rawValue)
                        if item.isNewRelease {
                            label(copy.newLabel, tint: theme.primaryText)
                        }
                    }

                    metadataButton(item.metadataLine)
                    metadataButton(item.posterName)

                    HStack(spacing: 8) {
                        proofChip(copy.likesTitle, value: item.likeCount)
                        proofChip(copy.commentLabel, value: item.commentCount)
                        proofChip(copy.repostLabel, value: item.repostCount)
                        proofChip(copy.savedSectionTitle, value: item.saveCount)
                    }

                    if !item.tags.isEmpty {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(item.tags, id: \.self) { tag in
                                    searchLabel("#\(tag)", tint: theme.tertiaryText, query: tag)
                                }
                            }
                        }
                    }

                    Text(item.caption)
                        .font(.subheadline)
                        .foregroundStyle(theme.secondaryText)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .transition(.move(edge: .top).combined(with: .opacity))
            }
        }
        .padding(14)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }

    private var jacket: some View {
        ZStack(alignment: .bottomLeading) {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(jacketGradient)
                .aspectRatio(1, contentMode: .fit)
                .overlay(alignment: .topTrailing) {
                    HStack(spacing: 8) {
                        Text(item.viralContextLine.uppercased())
                            .font(.caption2.weight(.black))
                            .tracking(1.2)
                            .foregroundStyle(coverBadgeForeground)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(coverBadgeBackground.opacity(0.92), in: Capsule())

                        Text(copy.postTypeEnglishLabel(item.postType))
                            .font(.caption2.weight(.black))
                            .tracking(1.5)
                            .foregroundStyle(coverBadgeForeground)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(coverBadgeBackground, in: Capsule())
                    }
                    .padding(14)
                }

            LinearGradient(
                colors: [.clear, coverGradientShadow],
                startPoint: .center,
                endPoint: .bottom
            )
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .allowsHitTesting(false)

            VStack(alignment: .leading, spacing: 6) {
                Image(systemName: jacketSymbol)
                    .font(.system(size: 30, weight: .bold))
                    .foregroundStyle(coverPrimaryText.opacity(0.95))
                Button {
                    onSearchTermTap?(item.title)
                } label: {
                    Text(item.title)
                        .font(.system(size: 28, weight: .black, design: titleDesign))
                        .foregroundStyle(coverPrimaryText)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                }
                .buttonStyle(.plain)

                Button {
                    onSearchTermTap?(item.creatorName)
                } label: {
                    Text(item.creatorName)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(coverSecondaryText)
                }
                .buttonStyle(.plain)
            }
            .padding(18)

            VStack {
                Spacer()
                HStack {
                    Spacer()
                    HStack(spacing: 8) {
                        compactActionButton(
                            title: actionCountText(item.likeCount),
                            systemImage: item.isLikedByUser ? "heart.fill" : "heart",
                            tint: item.isLikedByUser ? coverPrimaryText : coverPrimaryText.opacity(0.88)
                        ) {
                            withAnimation(.spring(duration: 0.25)) {
                                item.isLikedByUser.toggle()
                                item.likeCount = max(item.likeCount + (item.isLikedByUser ? 1 : -1), 0)
                            }
                        }

                        compactActionButton(
                            title: actionCountText(item.saveCount),
                            systemImage: item.isSavedByUser ? "bookmark.fill" : "bookmark",
                            tint: item.isSavedByUser ? coverPrimaryText : coverPrimaryText.opacity(0.88)
                        ) {
                            withAnimation(.spring(duration: 0.25)) {
                                item.isSavedByUser.toggle()
                                item.saveCount = max(item.saveCount + (item.isSavedByUser ? 1 : -1), 0)
                            }
                        }

                        compactActionButton(
                            title: actionCountText(item.shareCount),
                            systemImage: "paperplane",
                            tint: coverPrimaryText.opacity(0.88)
                        ) {
                            withAnimation(.spring(duration: 0.25)) {
                                item.shareCount += 1
                            }
                        }
                    }
                    .padding(14)
                }
            }
        }
    }

    private var jacketGradient: LinearGradient {
        switch item.postType {
        case .track:
            return LinearGradient(colors: [serviceColor.opacity(0.95), .black], startPoint: .topLeading, endPoint: .bottomTrailing)
        case .album:
            return LinearGradient(colors: [Color.white.opacity(0.20), serviceColor.opacity(0.88), .black], startPoint: .topLeading, endPoint: .bottomTrailing)
        case .playlist:
            return LinearGradient(colors: [Color.white.opacity(0.12), serviceColor.opacity(0.70), theme.cardRaised], startPoint: .topLeading, endPoint: .bottomTrailing)
        }
    }

    private var coverPrimaryText: Color {
        serviceColor.isPerceptuallyLight ? .black.opacity(0.92) : .white
    }

    private var coverUsesDarkText: Bool {
        serviceColor.isPerceptuallyLight
    }

    private var coverSecondaryText: Color {
        serviceColor.isPerceptuallyLight ? .black.opacity(0.66) : .white.opacity(0.82)
    }

    private var coverBadgeForeground: Color {
        serviceColor.isPerceptuallyLight ? .white : theme.background
    }

    private var coverBadgeBackground: Color {
        serviceColor.isPerceptuallyLight ? .black.opacity(0.82) : theme.primaryText
    }

    private var coverGradientShadow: Color {
        serviceColor.isPerceptuallyLight ? .white.opacity(0.12) : .black.opacity(theme.isDark ? 0.82 : 0.55)
    }

    private var jacketSymbol: String {
        switch item.postType {
        case .track: return "music.note"
        case .album: return "square.stack.fill"
        case .playlist: return "text.line.first.and.arrowtriangle.forward"
        }
    }

    private var serviceColor: Color {
        switch item.serviceName {
        case "Spotify": return theme.spotify
        case "Apple Music": return theme.appleMusic
        case "YouTube Music": return theme.youTubeMusic
        default: return theme.serviceDefault
        }
    }

    private func label(_ title: String, tint: Color) -> some View {
        Text(title)
            .font(.caption.weight(.bold))
            .foregroundStyle(tint)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(theme.chrome, in: Capsule())
            .overlay {
                if !theme.isDark {
                    Capsule().stroke(theme.line, lineWidth: 1)
                }
            }
    }

    private func searchLabel(_ title: String, tint: Color, query: String? = nil) -> some View {
        Button {
            onSearchTermTap?(query ?? title)
        } label: {
            label(title, tint: tint)
        }
        .buttonStyle(.plain)
    }

    private func metadataButton(_ text: String) -> some View {
        Button {
            onSearchTermTap?(text)
        } label: {
            Text(text)
                .font(.caption.weight(.semibold))
                .foregroundStyle(theme.tertiaryText)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .buttonStyle(.plain)
    }

    private func actionCountText(_ count: Int) -> String {
        max(count, 0).formatted(.number.notation(.compactName))
    }

    private func proofChip(_ title: String, value: Int) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(actionCountText(value))
                .font(.caption.weight(.black))
                .foregroundStyle(theme.primaryText)
            Text(title)
                .font(.caption2.weight(.bold))
                .foregroundStyle(theme.tertiaryText)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(theme.chromeStrong, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }

    private func compactActionButton(
        title: String,
        systemImage: String,
        tint: Color,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: systemImage)
                    .font(.caption.weight(.bold))
                Text(title)
                    .font(.caption.weight(.bold))
            }
            .foregroundStyle(tint)
            .padding(.horizontal, 10)
            .padding(.vertical, 8)
            .background(coverUsesDarkText ? .white.opacity(0.18) : .black.opacity(0.28), in: Capsule())
            .overlay {
                Capsule().stroke(coverUsesDarkText ? .black.opacity(0.12) : .white.opacity(0.14), lineWidth: 1)
            }
        }
        .buttonStyle(.plain)
    }
}

private extension Color {
    var isPerceptuallyLight: Bool {
        #if canImport(UIKit)
        let components = UIColor(self).cgColor.components ?? [0, 0, 0, 1]
        let resolved: (CGFloat, CGFloat, CGFloat) = {
            if components.count >= 3 {
                return (components[0], components[1], components[2])
            }
            let mono = components.first ?? 0
            return (mono, mono, mono)
        }()
        let luminance = (0.299 * resolved.0) + (0.587 * resolved.1) + (0.114 * resolved.2)
        return luminance > 0.66
        #else
        return false
        #endif
    }
}
