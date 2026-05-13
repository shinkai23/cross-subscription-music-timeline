//
//  SearchScreen.swift
//  MusicTimelineApp
//

import SwiftUI

struct SearchField: View {
    @Binding var text: String
    let theme: Theme
    let placeholder: String
    var onSubmit: (() -> Void)? = nil

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: "magnifyingglass")
                .foregroundStyle(theme.tertiaryText)
            TextField(placeholder, text: $text)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .foregroundStyle(theme.primaryText)
                .onSubmit { onSubmit?() }
            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundStyle(theme.tertiaryText)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 12)
        .background(theme.cardRaised, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }
}

struct FlowLayout<Data: RandomAccessCollection, Content: View>: View where Data.Element: Hashable {
    let data: Data
    let spacing: CGFloat
    let content: (Data.Element) -> Content

    var body: some View {
        VStack(alignment: .leading, spacing: spacing) {
            ForEach(Array(makeRows().enumerated()), id: \.offset) { _, row in
                HStack(spacing: spacing) {
                    ForEach(row, id: \.self) { element in
                        content(element)
                    }
                }
            }
        }
    }

    private func makeRows() -> [[Data.Element]] {
        var rows: [[Data.Element]] = [[]]
        var currentWidth: CGFloat = 0
        let maxWidth: CGFloat = 320

        for element in data {
            let estimatedWidth = CGFloat(String(describing: element).count * 9) + 42
            if currentWidth + estimatedWidth > maxWidth, !rows[rows.count - 1].isEmpty {
                rows.append([element])
                currentWidth = estimatedWidth + spacing
            } else {
                rows[rows.count - 1].append(element)
                currentWidth += estimatedWidth + spacing
            }
        }
        return rows
    }
}

struct SearchScreen: View {
    @AppStorage("recentSearches") private var recentSearchesRawValue = ""
    let items: [Item]
    @Binding var searchText: String
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    @Environment(\.dismiss) private var dismiss

    private var recentSearches: [String] {
        recentSearchesRawValue
            .split(separator: "|")
            .map(String.init)
            .filter { !$0.isEmpty }
    }

    private var filteredItems: [Item] {
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return [] }
        let lowercasedQuery = query.lowercased()
        return items.filter { item in
            item.searchableStrings.contains { $0.lowercased().contains(lowercasedQuery) }
        }
    }

    private var trendingTerms: [String] {
        let candidates = items.flatMap { [$0.title, $0.creatorName, $0.viralContextLine] + $0.tags.map { "#\($0)" } }
        var ordered: [String] = []
        for term in candidates where !ordered.contains(term) {
            ordered.append(term)
        }
        return Array(ordered.prefix(6))
    }

    var body: some View {
        NavigationStack {
            ZStack {
                theme.background.ignoresSafeArea()
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        SearchField(text: $searchText, theme: theme, placeholder: copy.searchPlaceholder, onSubmit: commitSearch)

                        if searchText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                            discovery
                        } else if filteredItems.isEmpty {
                            emptyResults
                        } else {
                            ForEach(filteredItems) { item in
                                TimelineCard(
                                    item: item,
                                    theme: theme,
                                    copy: copy,
                                    titleDesign: titleDesign,
                                    onSearchTermTap: applySearch
                                )
                            }
                        }
                    }
                    .padding(16)
                    .padding(.bottom, 24)
                }
            }
            .navigationTitle(copy.searchIconLabel)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(copy.done) { dismiss() }
                }
            }
        }
        .preferredColorScheme(theme.isDark ? .dark : .light)
    }

    private var discovery: some View {
        VStack(alignment: .leading, spacing: 20) {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Text(copy.searchHistoryTitle)
                        .font(.headline.weight(.bold))
                        .foregroundStyle(theme.primaryText)
                    Spacer()
                    if !recentSearches.isEmpty {
                        Button(copy.clearHistoryTitle) {
                            recentSearchesRawValue = ""
                        }
                        .font(.caption.weight(.bold))
                        .foregroundStyle(theme.secondaryText)
                    }
                }

                if recentSearches.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(copy.emptyHistoryTitle)
                            .font(.subheadline.weight(.bold))
                            .foregroundStyle(theme.primaryText)
                        Text(copy.emptyHistorySubtitle)
                            .font(.footnote)
                            .foregroundStyle(theme.secondaryText)
                    }
                    .padding(16)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(theme.card, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
                } else {
                    FlowLayout(data: recentSearches, spacing: 10) { term in
                        historyChip(term)
                    }
                }
            }

            VStack(alignment: .leading, spacing: 10) {
                Text(copy.searchTrendTitle)
                    .font(.headline.weight(.bold))
                    .foregroundStyle(theme.primaryText)
                Text(copy.searchTrendSubtitle)
                    .font(.footnote)
                    .foregroundStyle(theme.secondaryText)

                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                    ForEach(Array(trendingTerms.enumerated()), id: \.offset) { index, term in
                        Button {
                            applySearch(term)
                        } label: {
                            VStack(alignment: .leading, spacing: 12) {
                                Text(index.isMultiple(of: 2) ? "TREND" : "RISING")
                                    .font(.caption2.weight(.black))
                                    .tracking(1.3)
                                    .foregroundStyle(theme.tertiaryText)
                                Spacer()
                                Text(term)
                                    .font(.headline.weight(.bold))
                                    .foregroundStyle(theme.primaryText)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                            .padding(16)
                            .frame(height: index.isMultiple(of: 2) ? 128 : 156)
                            .background(
                                LinearGradient(
                                    colors: [theme.cardRaised, theme.card, index.isMultiple(of: 2) ? theme.spotify.opacity(0.45) : theme.appleMusic.opacity(0.40)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                ),
                                in: RoundedRectangle(cornerRadius: 24, style: .continuous)
                            )
                            .overlay {
                                RoundedRectangle(cornerRadius: 24, style: .continuous)
                                    .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
                            }
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
        }
    }

    private var emptyResults: some View {
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
    }

    private func historyChip(_ term: String) -> some View {
        Button {
            applySearch(term)
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "clock.arrow.circlepath")
                    .font(.caption.weight(.bold))
                Text(term)
                    .font(.subheadline.weight(.semibold))
            }
            .foregroundStyle(theme.primaryText)
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(theme.cardRaised, in: Capsule())
            .overlay {
                Capsule().stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.3)
            }
        }
        .buttonStyle(.plain)
    }

    private func commitSearch() {
        let query = searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return }
        storeRecentSearch(query)
    }

    private func applySearch(_ term: String) {
        searchText = term
        storeRecentSearch(term)
    }

    private func storeRecentSearch(_ term: String) {
        var updated = recentSearches.filter { $0.caseInsensitiveCompare(term) != .orderedSame }
        updated.insert(term, at: 0)
        recentSearchesRawValue = Array(updated.prefix(8)).joined(separator: "|")
    }
}
