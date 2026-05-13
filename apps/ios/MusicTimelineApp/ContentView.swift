//
//  ContentView.swift
//  MusicTimelineApp
//
//  Created by Sinkai I on 2026/05/06.
//

import SwiftUI
import SwiftData

struct ContentView: View {
    @AppStorage("themeMode") private var themeModeRawValue = ThemeMode.system.rawValue
    @AppStorage("appLanguage") private var appLanguageRawValue = AppLanguage.english.rawValue
    @AppStorage("hasCompletedSetup") private var hasCompletedSetup = false
    @AppStorage("signedInName") private var signedInName = ""
    @AppStorage("signInProvider") private var signInProviderRawValue = SignInProvider.apple.rawValue
    @AppStorage("fontStyle") private var fontStyleRawValue = FontStyleOption.rounded.rawValue
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
    @AppStorage("likesNotificationsEnabled") private var likesNotificationsEnabled = true
    @AppStorage("savesNotificationsEnabled") private var savesNotificationsEnabled = true
    @AppStorage("weeklyDigestEnabled") private var weeklyDigestEnabled = false

    @Environment(\.colorScheme) private var systemColorScheme
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Item.playedAt, order: .reverse) private var items: [Item]

    @State private var selectedRootTab: RootTab = .home
    @State private var selectedFeedTab: FeedTab = .recommended
    @State private var isShowingSearchScreen = false
    @State private var isShowingComposer = false
    @State private var isShowingSettings = false
    @State private var searchText = ""
    @State private var bottomBarHiddenProgress: CGFloat = 0

    private var themeMode: ThemeMode {
        ThemeMode(rawValue: themeModeRawValue) ?? .system
    }

    private var appLanguage: AppLanguage {
        AppLanguage(rawValue: appLanguageRawValue) ?? .english
    }

    private var signInProvider: SignInProvider {
        SignInProvider(rawValue: signInProviderRawValue) ?? .apple
    }

    private var fontStyle: FontStyleOption {
        FontStyleOption(rawValue: fontStyleRawValue) ?? .rounded
    }

    private var activeTheme: Theme {
        switch themeMode {
        case .system:
            return systemColorScheme == .dark ? .dark : .light
        case .dark:
            return .dark
        case .light:
            return .light
        }
    }

    private var copy: Copybook {
        Copybook(language: appLanguage)
    }

    private var titleDesign: Font.Design {
        fontStyle.fontDesign
    }

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottom) {
                activeTheme.background
                    .ignoresSafeArea()

                if hasCompletedSetup {
                    currentScreen
                } else {
                    SetupView(
                        themeMode: Binding(
                            get: { themeMode },
                            set: { themeModeRawValue = $0.rawValue }
                        ),
                        language: Binding(
                            get: { appLanguage },
                            set: { appLanguageRawValue = $0.rawValue }
                        ),
                        signedInName: $signedInName,
                        signInProvider: Binding(
                            get: { signInProvider },
                            set: { signInProviderRawValue = $0.rawValue }
                        ),
                        theme: activeTheme,
                        copy: copy,
                        titleDesign: titleDesign
                    ) {
                        hasCompletedSetup = true
                        if items.isEmpty {
                            insertSampleTimeline()
                        }
                    }
                }

                if hasCompletedSetup {
                    BottomTabBar(
                        selectedTab: $selectedRootTab,
                        theme: activeTheme,
                        copy: copy,
                        hiddenProgress: bottomBarHiddenProgress
                    ) {
                        isShowingComposer = true
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 10)
                }
            }
        }
        .tint(activeTheme.toolbarTint)
        .preferredColorScheme(themeMode.preferredColorScheme)
        .toolbarBackground(activeTheme.background, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
        .sheet(isPresented: $isShowingSearchScreen) {
            SearchScreen(
                items: items,
                searchText: $searchText,
                theme: activeTheme,
                copy: copy,
                titleDesign: titleDesign
            )
        }
        .sheet(isPresented: $isShowingComposer) {
            ComposerView(
                signedInName: signedInName,
                theme: activeTheme,
                copy: copy
            ) { draft in
                submitPost(draft)
            }
        }
        .sheet(isPresented: $isShowingSettings) {
            AccountSettingsView(
                themeMode: Binding(
                    get: { themeMode },
                    set: { themeModeRawValue = $0.rawValue }
                ),
                language: Binding(
                    get: { appLanguage },
                    set: { appLanguageRawValue = $0.rawValue }
                ),
                signedInName: $signedInName,
                signInProvider: Binding(
                    get: { signInProvider },
                    set: { signInProviderRawValue = $0.rawValue }
                ),
                fontStyle: Binding(
                    get: { fontStyle },
                    set: { fontStyleRawValue = $0.rawValue }
                ),
                notificationsEnabled: $notificationsEnabled,
                likesNotificationsEnabled: $likesNotificationsEnabled,
                savesNotificationsEnabled: $savesNotificationsEnabled,
                weeklyDigestEnabled: $weeklyDigestEnabled,
                theme: activeTheme,
                copy: copy
            )
            .presentationDetents([.medium, .large])
        }
    }

    @ViewBuilder
    private var currentScreen: some View {
        switch selectedRootTab {
        case .home, .compose:
            TimelineFeedScreen(
                items: items,
                selectedFeedTab: $selectedFeedTab,
                theme: activeTheme,
                copy: copy,
                titleDesign: titleDesign,
                signedInName: signedInName,
                signInProvider: signInProvider,
                onOpenSearch: { openSearch() },
                onOpenSearchTerm: { term in
                    openSearch(term: term)
                },
                onMetricsChange: { bottomBarHiddenProgress = $0 }
            )
        case .likes:
            LikesHubView(
                items: items,
                theme: activeTheme,
                copy: copy,
                titleDesign: titleDesign,
                onMetricsChange: { bottomBarHiddenProgress = $0 }
            )
        case .account:
            AccountHomeView(
                signedInName: signedInName,
                signInProvider: signInProvider,
                themeMode: themeMode,
                language: appLanguage,
                fontStyle: fontStyle,
                notificationsEnabled: notificationsEnabled,
                likesNotificationsEnabled: likesNotificationsEnabled,
                savesNotificationsEnabled: savesNotificationsEnabled,
                weeklyDigestEnabled: weeklyDigestEnabled,
                items: items,
                theme: activeTheme,
                copy: copy,
                titleDesign: titleDesign,
                onOpenSettings: { isShowingSettings = true }
            )
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 96)
            .onAppear {
                bottomBarHiddenProgress = 0
            }
        }
    }

    private func insertSampleTimeline() {
        withAnimation(.spring(duration: 0.4)) {
            for item in Item.sampleTimeline {
                modelContext.insert(item)
            }
        }
    }

    private func submitPost(_ draft: PostDraft) {
        let trimmedName = signedInName.trimmingCharacters(in: .whitespacesAndNewlines)
        let posterName = trimmedName.isEmpty ? "@musicfan" : "@\(trimmedName)"
        let item = Item(
            serviceName: draft.serviceName,
            postType: draft.postType,
            title: draft.title,
            creatorName: draft.artistName,
            posterName: posterName,
            metadataLine: draft.metadataLine,
            caption: draft.caption,
            tags: draft.tags,
            isFromFollowing: true,
            isNewRelease: draft.isNewRelease,
            isLikedByUser: false,
            isSavedByUser: false,
            isOwnedByCurrentUser: true,
            playedAt: .now,
            likeCount: 0,
            saveCount: 0,
            commentCount: 0,
            repostCount: 0,
            shareCount: 0
        )

        withAnimation(.spring(duration: 0.3)) {
            modelContext.insert(item)
            selectedRootTab = .home
            selectedFeedTab = draft.isNewRelease ? .newReleases : .recommended
        }
    }

    private func openSearch() {
        isShowingSearchScreen = true
    }

    private func openSearch(term: String) {
        searchText = normalizedSearchTerm(term)
        isShowingSearchScreen = true
    }

    private func normalizedSearchTerm(_ term: String) -> String {
        term
            .replacingOccurrences(of: "#", with: "")
            .replacingOccurrences(of: "·", with: " ")
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
#Preview("Timeline Home") {
    PreviewTimelineHome()
}

#Preview("First Setup") {
    PreviewSetupScreen()
}

private struct PreviewTimelineHome: View {
    private let container: ModelContainer = PreviewData.makeContainer(withSamples: true)

    init() {
        PreviewDefaults.applyTimelineState()
    }

    var body: some View {
        ContentView()
            .modelContainer(container)
    }
}

private struct PreviewSetupScreen: View {
    private let container: ModelContainer = PreviewData.makeContainer(withSamples: false)

    init() {
        PreviewDefaults.applySetupState()
    }

    var body: some View {
        ContentView()
            .modelContainer(container)
    }
}

private enum PreviewDefaults {
    static func applyTimelineState() {
        let defaults = UserDefaults.standard
        defaults.set(ThemeMode.dark.rawValue, forKey: "themeMode")
        defaults.set(AppLanguage.english.rawValue, forKey: "appLanguage")
        defaults.set(true, forKey: "hasCompletedSetup")
        defaults.set("sinkaii", forKey: "signedInName")
        defaults.set(SignInProvider.spotify.rawValue, forKey: "signInProvider")
        defaults.set(FontStyleOption.rounded.rawValue, forKey: "fontStyle")
        defaults.set(true, forKey: "notificationsEnabled")
        defaults.set(true, forKey: "likesNotificationsEnabled")
        defaults.set(true, forKey: "savesNotificationsEnabled")
        defaults.set(false, forKey: "weeklyDigestEnabled")
        defaults.set("Frank Ocean|#night-drive|SZA", forKey: "recentSearches")
    }

    static func applySetupState() {
        let defaults = UserDefaults.standard
        defaults.set(ThemeMode.light.rawValue, forKey: "themeMode")
        defaults.set(AppLanguage.japanese.rawValue, forKey: "appLanguage")
        defaults.set(false, forKey: "hasCompletedSetup")
        defaults.set("", forKey: "signedInName")
        defaults.set(SignInProvider.apple.rawValue, forKey: "signInProvider")
        defaults.set(FontStyleOption.rounded.rawValue, forKey: "fontStyle")
        defaults.set(true, forKey: "notificationsEnabled")
        defaults.set(true, forKey: "likesNotificationsEnabled")
        defaults.set(true, forKey: "savesNotificationsEnabled")
        defaults.set(false, forKey: "weeklyDigestEnabled")
        defaults.set("", forKey: "recentSearches")
    }
}

private enum PreviewData {
    static func makeContainer(withSamples: Bool) -> ModelContainer {
        let schema = Schema([Item.self])
        let configuration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: true)

        do {
            let container = try ModelContainer(for: schema, configurations: [configuration])
            if withSamples {
                for item in Item.sampleTimeline {
                    container.mainContext.insert(item)
                }
            }
            return container
        } catch {
            fatalError("Could not create preview container: \(error)")
        }
    }
}
