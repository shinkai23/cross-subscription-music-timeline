//
//  TimelineFeedScreen.swift
//  MusicTimelineApp
//

import SwiftUI
import SwiftData

struct TimelineFeedScreen: View {
    let items: [Item]
    @Binding var selectedFeedTab: FeedTab
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    let signedInName: String
    let signInProvider: SignInProvider
    let onOpenSearch: () -> Void
    let onOpenSearchTerm: (String) -> Void
    let onMetricsChange: (CGFloat) -> Void

    @State private var previousOffset: CGFloat = 0
    @State private var headerCollapseProgress: CGFloat = 0

    private var visibleItems: [Item] {
        items.filter(matchesSelectedFeedTab)
    }

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 20, pinnedViews: [.sectionHeaders]) {
                GeometryReader { proxy in
                    Color.clear
                        .preference(key: FeedOffsetPreferenceKey.self, value: proxy.frame(in: .named("timelineScroll")).minY)
                }
                .frame(height: 0)

                Section {
                    VStack(alignment: .leading, spacing: 20) {
                        intro

                        if visibleItems.isEmpty {
                            emptyState
                        } else {
                            ForEach(Array(visibleItems.enumerated()), id: \.element.id) { index, item in
                                if index == 1 {
                                    FeaturedRail(
                                        items: visibleItems,
                                        theme: theme,
                                        copy: copy,
                                        titleDesign: titleDesign,
                                        onSearchTermTap: onOpenSearchTerm
                                    )
                                }
                                TimelineCard(
                                    item: item,
                                    theme: theme,
                                    copy: copy,
                                    titleDesign: titleDesign,
                                    onSearchTermTap: onOpenSearchTerm
                                )
                            }
                        }
                    }
                } header: {
                    header
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 96)
        }
        .coordinateSpace(name: "timelineScroll")
        .onPreferenceChange(FeedOffsetPreferenceKey.self) { value in
            let delta = value - previousOffset
            let direction: ScrollDirection
            if delta < -1 {
                direction = .down
            } else if delta > 1 {
                direction = .up
            } else {
                direction = .idle
            }
            previousOffset = value
            let progress: CGFloat
            switch direction {
            case .down:
                progress = min(max((-value - 24) / 90, 0), 1)
            case .up, .idle:
                progress = 0
            }
            headerCollapseProgress = min(max((-value - 12) / 56, 0), 1)
            onMetricsChange(progress)
        }
        .simultaneousGesture(
            DragGesture(minimumDistance: 24)
                .onEnded { gesture in
                    let horizontal = gesture.translation.width
                    let vertical = gesture.translation.height
                    guard abs(horizontal) > abs(vertical), abs(horizontal) > 50 else { return }
                    shiftFeedTab(horizontal < 0 ? 1 : -1)
                }
        )
    }

    private var intro: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(copy.appTitle)
                .font(.system(size: 28, weight: .black, design: titleDesign))
                .foregroundStyle(theme.primaryText)

            Text(copy.discover)
                .font(.caption.weight(.black))
                .tracking(2)
                .foregroundStyle(theme.secondaryText)

            Text(copy.discoverDescription)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(theme.tertiaryText)

            if !signedInName.isEmpty {
                HStack(spacing: 8) {
                    Text(copy.signInSummary)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(theme.tertiaryText)
                    Text(signedInName)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(theme.primaryText)
                    Text("· \(copy.providerName(signInProvider))")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(theme.secondaryText)
                }
            }
        }
    }

    private var header: some View {
        FeedTabStrip(
            selectedTab: $selectedFeedTab,
            theme: theme,
            copy: copy,
            collapseProgress: headerCollapseProgress,
            onSearchTap: onOpenSearch
        )
            .padding(.vertical, 8)
            .background {
                Rectangle()
                    .fill(theme.background.opacity(theme.isDark ? 0.08 + (headerCollapseProgress * 0.24) : 0.18 + (headerCollapseProgress * 0.28)))
                    .overlay(.ultraThinMaterial.opacity(headerCollapseProgress))
            }
    }

    private var emptyState: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(copy.noMatches)
                .font(.title3.weight(.bold))
                .foregroundStyle(theme.primaryText)
            Text(copy.noMatchesDescription)
                .font(.subheadline)
                .foregroundStyle(theme.secondaryText)
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }

    private func matchesSelectedFeedTab(_ item: Item) -> Bool {
        switch selectedFeedTab {
        case .all:
            return true
        case .newReleases:
            return item.isNewRelease
        case .following:
            return item.isFromFollowing
        case .recommended:
            return !item.isFromFollowing || item.likeCount >= 250 || item.saveCount >= 100
        }
    }

    private func shiftFeedTab(_ delta: Int) {
        guard let currentIndex = FeedTab.allCases.firstIndex(of: selectedFeedTab) else { return }
        let newIndex = min(max(currentIndex + delta, 0), FeedTab.allCases.count - 1)
        guard newIndex != currentIndex else { return }
        withAnimation(.spring(duration: 0.28)) {
            selectedFeedTab = FeedTab.allCases[newIndex]
        }
    }
}
