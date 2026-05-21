//
//  AppModels.swift
//  MusicTimelineApp
//

import SwiftUI

enum ThemeMode: String, CaseIterable, Identifiable {
    case system
    case dark
    case light

    var id: String { rawValue }

    var preferredColorScheme: ColorScheme? {
        switch self {
        case .system:
            return nil
        case .dark:
            return .dark
        case .light:
            return .light
        }
    }
}

enum AppLanguage: String, CaseIterable, Identifiable {
    case english
    case japanese

    var id: String { rawValue }
}

enum SignInProvider: String, CaseIterable, Identifiable {
    case apple
    case spotify
    case google

    var id: String { rawValue }
}

enum FeedTab: String, CaseIterable, Identifiable {
    case all
    case newReleases
    case following
    case recommended

    var id: String { rawValue }
}

enum RootTab: String, CaseIterable, Identifiable {
    case home
    case compose
    case likes
    case account

    var id: String { rawValue }
}

enum LikesSection: String, CaseIterable, Identifiable {
    case liked
    case saved
    case activity

    var id: String { rawValue }
}

enum FontStyleOption: String, CaseIterable, Identifiable {
    case rounded
    case defaultStyle
    case serif

    var id: String { rawValue }

    var fontDesign: Font.Design {
        switch self {
        case .rounded:
            return .rounded
        case .defaultStyle:
            return .default
        case .serif:
            return .serif
        }
    }
}

struct FeedScrollMetrics: Equatable {
    var offset: CGFloat = 0
    var direction: ScrollDirection = .idle
}

enum ScrollDirection {
    case up
    case down
    case idle
}

struct FeedOffsetPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0

    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

struct PostDraft {
    var title = ""
    var artistName = ""
    var caption = ""
    var serviceName = "Spotify"
    var postType: MusicPostType = .track
    var metadataLine = "Track"
    var tagsText = ""
    var isNewRelease = false
    var sourceLibraryID = ""
    var shareHook = ""
    var selectedMoments: [String] = []

    var tags: [String] {
        let manualTags = tagsText
            .split(separator: ",")
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }

        return Array(Set(manualTags + selectedMoments)).sorted()
    }
}

struct ActivityNotification: Identifiable {
    let id = UUID()
    let title: String
    let body: String
    let symbolName: String
    let timestamp: String
}

struct SubscriptionLibraryAsset: Identifiable, Hashable {
    let id: String
    let serviceName: String
    let postType: MusicPostType
    let title: String
    let creatorName: String
    let metadataLine: String
    let captionSeed: String
    let tags: [String]
    let momentumLabel: String

    static let mockLibrary: [SubscriptionLibraryAsset] = [
        SubscriptionLibraryAsset(
            id: "spotify-track-nights",
            serviceName: "Spotify",
            postType: .track,
            title: "Nights",
            creatorName: "Frank Ocean",
            metadataLine: "Track • Blonde",
            captionSeed: "Everybody knows the beat switch. The post only works if the feeling around it is specific.",
            tags: ["late-night", "drive", "frank-ocean"],
            momentumLabel: "Late-night staple"
        ),
        SubscriptionLibraryAsset(
            id: "spotify-track-saturn",
            serviceName: "Spotify",
            postType: .track,
            title: "Saturn",
            creatorName: "SZA",
            metadataLine: "Track • New Release",
            captionSeed: "Fresh drop energy. This is the kind of post people save before they even finish the track.",
            tags: ["new", "sza", "fresh"],
            momentumLabel: "Saving fast"
        ),
        SubscriptionLibraryAsset(
            id: "spotify-playlist-after-dark",
            serviceName: "Spotify",
            postType: .playlist,
            title: "After Dark Drive",
            creatorName: "You",
            metadataLine: "Playlist • 32 tracks",
            captionSeed: "A personal sequence hits harder when the transitions tell a story instead of listing songs.",
            tags: ["playlist", "night-drive", "personal"],
            momentumLabel: "Personal playlist"
        ),
        SubscriptionLibraryAsset(
            id: "apple-album-ctrl",
            serviceName: "Apple Music",
            postType: .album,
            title: "Ctrl",
            creatorName: "SZA",
            metadataLine: "Album • 14 tracks",
            captionSeed: "Album posts travel when they frame a full listen as a mood, not a review.",
            tags: ["album-run", "rnb", "sza"],
            momentumLabel: "Full-album pull"
        ),
        SubscriptionLibraryAsset(
            id: "apple-playlist-summer",
            serviceName: "Apple Music",
            postType: .playlist,
            title: "Summer Rotation",
            creatorName: "Editorial Team",
            metadataLine: "Playlist • Recommended For You",
            captionSeed: "Editorial picks spread when the first three songs instantly explain why the playlist exists.",
            tags: ["recommended", "summer", "pop"],
            momentumLabel: "Editorial pick"
        ),
        SubscriptionLibraryAsset(
            id: "youtube-playlist-tokyo",
            serviceName: "YouTube Music",
            postType: .playlist,
            title: "Tokyo Night Ride",
            creatorName: "You",
            metadataLine: "Playlist • 27 saves",
            captionSeed: "A custom playlist has to feel like a world. Give people a reason to screenshot it.",
            tags: ["playlist", "city-pop", "night-drive"],
            momentumLabel: "Screenshot bait"
        ),
        SubscriptionLibraryAsset(
            id: "youtube-track-after-hours",
            serviceName: "YouTube Music",
            postType: .track,
            title: "After Hours",
            creatorName: "The Weeknd",
            metadataLine: "Track • After Hours",
            captionSeed: "Short posts on already-loved tracks work best when the context is ridiculously sharp.",
            tags: ["synth", "night", "the-weeknd"],
            momentumLabel: "Always clickable"
        )
    ]

    static func assets(for serviceName: String) -> [SubscriptionLibraryAsset] {
        mockLibrary.filter { $0.serviceName == serviceName }
    }
}

struct Copybook {
    let language: AppLanguage

    var appTitle: String { text(en: "Music Timeline", ja: "音楽タイムライン") }
    var settings: String { text(en: "Settings", ja: "設定") }
    var done: String { text(en: "Done", ja: "完了") }
    var appearance: String { text(en: "Appearance", ja: "表示") }
    var languageTitle: String { text(en: "Language", ja: "言語") }
    var account: String { text(en: "Account", ja: "アカウント") }
    var themeTitle: String { text(en: "Theme", ja: "テーマ") }
    var fontTitle: String { text(en: "Font", ja: "フォント") }
    var notificationsTitle: String { text(en: "Notifications", ja: "通知") }
    var profileTitle: String { text(en: "Profile", ja: "プロフィール") }
    var musicFeed: String { text(en: "MUSIC FEED", ja: "ミュージックフィード") }
    var noPosts: String { text(en: "No posts yet.", ja: "まだ投稿がありません。") }
    var loadDemoDescription: String { text(en: "Load demo posts to preview a jacket-first timeline.", ja: "ジャケット中心のタイムラインをデモ投稿で確認できます。") }
    var loadDemoTimeline: String { text(en: "Load Demo Timeline", ja: "デモタイムラインを読み込む") }
    var discover: String { text(en: "DISCOVER", ja: "見つける") }
    var discoverDescription: String { text(en: "Search tags, posters, artists, and tracks.", ja: "タグ、投稿者、アーティスト、曲を検索できます。") }
    var searchPlaceholder: String { text(en: "Search tags, poster, artist, title...", ja: "タグ、投稿者、アーティスト、タイトルを検索") }
    var noMatches: String { text(en: "No matching posts.", ja: "一致する投稿がありません。") }
    var noMatchesDescription: String { text(en: "Try another tag, poster name, artist, or switch tabs.", ja: "別のタグ、投稿者名、アーティスト名を試すか、タブを切り替えてください。") }
    var deletePost: String { text(en: "Delete Post", ja: "投稿を削除") }
    var setupEyebrow: String { text(en: "FIRST SETUP", ja: "初期セットアップ") }
    var setupTitle: String { text(en: "Choose your theme, language, and sign in.", ja: "テーマ、言語、サインインを設定しましょう。") }
    var setupDescription: String { text(en: "Start with the mode that fits your feed habits. You can change this later in settings.", ja: "使い方に合わせて最初の表示を選べます。あとから設定で変更できます。") }
    var signInTitle: String { text(en: "Sign In", ja: "サインイン") }
    var displayNameTitle: String { text(en: "Display Name", ja: "表示名") }
    var displayNamePlaceholder: String { text(en: "Your profile name", ja: "プロフィール名") }
    var providerTitle: String { text(en: "Provider", ja: "連携先") }
    var continueTitle: String { text(en: "Continue", ja: "はじめる") }
    var signInSummary: String { text(en: "Signed in as", ja: "サインイン中") }
    var systemTheme: String { text(en: "System", ja: "システム") }
    var darkTheme: String { text(en: "Dark", ja: "ダーク") }
    var lightTheme: String { text(en: "Light", ja: "ライト") }
    var english: String { text(en: "English", ja: "英語") }
    var japanese: String { text(en: "Japanese", ja: "日本語") }
    var apple: String { text(en: "Apple", ja: "Apple") }
    var spotify: String { text(en: "Spotify", ja: "Spotify") }
    var google: String { text(en: "Google", ja: "Google") }
    var track: String { text(en: "Track", ja: "曲") }
    var album: String { text(en: "Album", ja: "アルバム") }
    var playlist: String { text(en: "Playlist", ja: "プレイリスト") }
    var newLabel: String { text(en: "New", ja: "新着") }
    var likesTitle: String { text(en: "Likes", ja: "いいね") }
    var homeShort: String { text(en: "Home", ja: "ホーム") }
    var composeShort: String { text(en: "Post", ja: "プラス") }
    var accountShort: String { text(en: "Account", ja: "アカウント") }
    var likesEmpty: String { text(en: "No liked posts yet.", ja: "まだいいねした投稿がありません。") }
    var likesEmptyDescription: String { text(en: "Tap the heart on any post and it will appear here.", ja: "投稿のハートを押すとここに表示されます。") }
    var accountDescription: String { text(en: "Profile, language, font, theme, and notifications.", ja: "プロフィール、言語、フォント、テーマ、通知を管理できます。") }
    var searchIconLabel: String { text(en: "Search", ja: "検索") }
    var featuredRailTitle: String { text(en: "Rock Picks", ja: "ロックなおすすめ") }
    var featuredRailSubtitle: String { text(en: "Swipe through louder moods between posts.", ja: "投稿の合間に、気分を変えるおすすめを。") }
    var likedHighlightsTitle: String { text(en: "Replay your favorites", ja: "お気に入りを見返す") }
    var likedHighlightsSubtitle: String { text(en: "Quickly jump back into the posts you keep touching.", ja: "何度も触れた投稿をすぐに見返せます。") }
    var savedHighlightsTitle: String { text(en: "Saved for later", ja: "あとで聴く") }
    var savedHighlightsSubtitle: String { text(en: "A shelf for the ones worth revisiting when the mood changes.", ja: "気分が変わった時に戻りたい投稿をまとめました。") }
    var activityEmptyTitle: String { text(en: "No reactions yet.", ja: "まだ反応はありません。") }
    var activityEmptySubtitle: String { text(en: "When your posts get likes, saves, or shares, they will appear here.", ja: "あなたの投稿にいいねや保存、共有が付くとここに表示されます。") }
    var profileStatsTitle: String { text(en: "Profile snapshot", ja: "プロフィール概要") }
    var preferenceTitle: String { text(en: "Preferences", ja: "設定の概要") }
    var openSettingsTitle: String { text(en: "Open settings", ja: "設定を開く") }
    var previewCardTitle: String { text(en: "Live cover preview", ja: "カバープレビュー") }
    var quickTagsTitle: String { text(en: "Quick tags", ja: "おすすめタグ") }
    var sourceLibraryTitle: String { text(en: "Pick from your library", ja: "ライブラリから選択") }
    var sourceLibrarySubtitle: String { text(en: "Choose a real track from the selected subscription and build the post around it.", ja: "選んだサブスク内の実在する曲を起点に投稿を組み立てます。") }
    var hookTitle: String { text(en: "Why people will share this", ja: "広がる理由") }
    var hookPlaceholder: String { text(en: "What is the angle, scene, or feeling people will instantly get?", ja: "どんな場面や感情が一瞬で伝わるか") }
    var postMomentsTitle: String { text(en: "Moments to anchor it", ja: "結びつける瞬間") }
    var publishPostTitle: String { text(en: "Publish", ja: "投稿する") }
    var requiredFieldHint: String { text(en: "Title and artist are required.", ja: "タイトルとアーティスト名は必須です。") }
    var notificationsOff: String { text(en: "Off", ja: "オフ") }
    var likesNotificationsTitle: String { text(en: "Likes on my posts", ja: "自分の投稿へのいいね") }
    var savesNotificationsTitle: String { text(en: "Saves on my posts", ja: "自分の投稿の保存") }
    var digestNotificationsTitle: String { text(en: "Weekly digest", ja: "週間ダイジェスト") }
    var searchPromptTitle: String { text(en: "Find songs, posters, and moods", ja: "曲、投稿者、気分を見つける") }
    var profileMemberSince: String { text(en: "Posting from your personal lane.", ja: "自分のレーンから投稿中。") }
    var creatorSignalsTitle: String { text(en: "Creator signals", ja: "クリエイター指標") }
    var creatorSignalsSubtitle: String { text(en: "The strongest posts feel personal, save-worthy, and instantly legible.", ja: "強い投稿は、個人的で、保存したくなり、ひと目で伝わります。") }
    var trendingPulseTitle: String { text(en: "Moving fast", ja: "伸びている投稿") }
    var communityCutTitle: String { text(en: "Your taste network", ja: "あなたの周辺で人気") }
    var searchJumpTitle: String { text(en: "Tap through the graph", ja: "関係するワードへ飛ぶ") }
    var searchHistoryTitle: String { text(en: "Recent searches", ja: "最近の検索") }
    var searchTrendTitle: String { text(en: "Trending now", ja: "最近のトレンド") }
    var searchTrendSubtitle: String { text(en: "Tap a card to jump straight into it.", ja: "気になるカードをタップして、そのまま検索できます。") }
    var clearHistoryTitle: String { text(en: "Clear", ja: "クリア") }
    var emptyHistoryTitle: String { text(en: "No history yet", ja: "履歴はまだありません") }
    var emptyHistorySubtitle: String { text(en: "Search artists, playlists, or moods and they will land here.", ja: "アーティストやプレイリスト、気分を検索するとここに残ります。") }
    var likedSectionTitle: String { text(en: "Liked tracks", ja: "いいねした曲") }
    var savedSectionTitle: String { text(en: "Saved picks", ja: "保存済み") }
    var activitySectionTitle: String { text(en: "Activity", ja: "通知") }
    var composeSectionTitle: String { text(en: "Post", ja: "投稿") }
    var commentLabel: String { text(en: "Comments", ja: "コメント") }
    var repostLabel: String { text(en: "Reposts", ja: "リポスト") }

    func tabTitle(_ tab: FeedTab) -> String {
        switch tab {
        case .all: return text(en: "All", ja: "全て")
        case .newReleases: return text(en: "New", ja: "新着")
        case .following: return text(en: "Following", ja: "フォロー中")
        case .recommended: return text(en: "Recommended", ja: "おすすめ")
        }
    }

    func rootTitle(_ tab: RootTab) -> String {
        switch tab {
        case .home: return homeShort
        case .compose: return composeShort
        case .likes: return likesTitle
        case .account: return accountShort
        }
    }

    func likesSectionTitle(_ section: LikesSection) -> String {
        switch section {
        case .liked: return likedSectionTitle
        case .saved: return savedSectionTitle
        case .activity: return activitySectionTitle
        }
    }

    func themeTitle(_ mode: ThemeMode) -> String {
        switch mode {
        case .system: return systemTheme
        case .dark: return darkTheme
        case .light: return lightTheme
        }
    }

    func languageName(_ language: AppLanguage) -> String {
        switch language {
        case .english: return english
        case .japanese: return japanese
        }
    }

    func providerName(_ provider: SignInProvider) -> String {
        switch provider {
        case .apple: return apple
        case .spotify: return spotify
        case .google: return google
        }
    }

    func postTypeLabel(_ type: MusicPostType) -> String {
        switch type {
        case .track: return track
        case .album: return album
        case .playlist: return playlist
        }
    }

    func postTypeEnglishLabel(_ type: MusicPostType) -> String {
        switch type {
        case .track: return "TRACK"
        case .album: return "ALBUM"
        case .playlist: return "PLAYLIST"
        }
    }

    func fontTitle(_ option: FontStyleOption) -> String {
        switch option {
        case .rounded: return text(en: "Rounded", ja: "Rounded")
        case .defaultStyle: return text(en: "System", ja: "System")
        case .serif: return text(en: "Serif", ja: "Serif")
        }
    }

    private func text(en: String, ja: String) -> String {
        switch language {
        case .english: return en
        case .japanese: return ja
        }
    }
}
