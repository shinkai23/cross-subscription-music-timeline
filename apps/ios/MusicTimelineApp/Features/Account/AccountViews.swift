//
//  AccountViews.swift
//  MusicTimelineApp
//

import SwiftUI

struct AccountHomeView: View {
    let signedInName: String
    let signInProvider: SignInProvider
    let themeMode: ThemeMode
    let language: AppLanguage
    let fontStyle: FontStyleOption
    let notificationsEnabled: Bool
    let likesNotificationsEnabled: Bool
    let savesNotificationsEnabled: Bool
    let weeklyDigestEnabled: Bool
    let items: [Item]
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    let onOpenSettings: () -> Void
    let onLogout: () -> Void
    @State private var isShowingSpotifyConnect = false
    @State private var providerAccounts: [ProviderAccountDTO] = []
    @State private var isLoadingProviderAccounts = false
    @State private var providerAccountsError: String?

    private var ownedItems: [Item] {
        items.filter(\.isOwnedByCurrentUser)
    }

    private var totalLikes: Int {
        ownedItems.reduce(0) { $0 + $1.likeCount }
    }

    private var totalSaves: Int {
        ownedItems.reduce(0) { $0 + $1.saveCount }
    }

    private var totalReposts: Int {
        ownedItems.reduce(0) { $0 + $1.repostCount }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                profileHero
                spotifyConnection
                logoutButton
                preferenceGrid
                creatorSignalsCard

                AccountInfoCard(
                    rows: [
                        (copy.themeTitle, copy.themeTitle(themeMode)),
                        (copy.languageTitle, copy.languageName(language)),
                        (copy.fontTitle, copy.fontTitle(fontStyle)),
                        (copy.notificationsTitle, notificationsEnabled ? copy.done : copy.notificationsOff),
                        (copy.likesNotificationsTitle, likesNotificationsEnabled ? copy.done : copy.notificationsOff),
                        (copy.savesNotificationsTitle, savesNotificationsEnabled ? copy.done : copy.notificationsOff),
                        (copy.digestNotificationsTitle, weeklyDigestEnabled ? copy.done : copy.notificationsOff)
                    ],
                    theme: theme
                )
            }
        }
        .sheet(isPresented: $isShowingSpotifyConnect) {
            SpotifyConnectView { response in
                UserDefaults.standard.set(
                    response.providerUserId,
                    forKey: "provider.spotify.providerUserId"
                )
                Task {
                    await loadProviderAccounts()
                }
            }
        }
        .task {
            await loadProviderAccounts()
        }
    }

    private var creatorSignalsCard: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(copy.creatorSignalsTitle)
                .font(.headline.weight(.bold))
                .foregroundStyle(theme.primaryText)
            Text(copy.creatorSignalsSubtitle)
                .font(.subheadline)
                .foregroundStyle(theme.secondaryText)

            HStack(spacing: 12) {
                signalTile(value: ownedItems.count.formatted(), title: copy.composeSectionTitle)
                signalTile(value: totalLikes.formatted(.number.notation(.compactName)), title: copy.likesTitle)
                signalTile(value: totalSaves.formatted(.number.notation(.compactName)), title: copy.savedSectionTitle)
                signalTile(value: totalReposts.formatted(.number.notation(.compactName)), title: copy.repostLabel)
            }
        }
        .padding(18)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.4)
        }
    }

    private var profileHero: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .top, spacing: 14) {
                Image(systemName: "person.crop.circle.fill")
                    .font(.system(size: 58))
                    .foregroundStyle(theme.primaryText)

                VStack(alignment: .leading, spacing: 6) {
                    Text(signedInName.isEmpty ? "musicfan" : signedInName)
                        .font(.system(size: 30, weight: .black, design: titleDesign))
                        .foregroundStyle(theme.primaryText)
                    Text(copy.providerName(signInProvider))
                        .font(.headline.weight(.semibold))
                        .foregroundStyle(theme.secondaryText)
                    Text(copy.profileMemberSince)
                        .font(.subheadline)
                        .foregroundStyle(theme.tertiaryText)
                }

                Spacer()

                Button(action: onOpenSettings) {
                    Label(copy.openSettingsTitle, systemImage: "gearshape.fill")
                        .labelStyle(.iconOnly)
                        .font(.headline)
                        .foregroundStyle(theme.primaryText)
                        .frame(width: 42, height: 42)
                        .background(theme.chromeStrong, in: Circle())
                }
                .buttonStyle(.plain)
            }

            Text(copy.accountDescription)
                .font(.subheadline)
                .foregroundStyle(theme.secondaryText)
        }
    }

    private var preferenceGrid: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(copy.profileStatsTitle)
                .font(.headline.weight(.bold))
                .foregroundStyle(theme.primaryText)

            HStack(spacing: 12) {
                preferencePill(title: copy.themeTitle, value: copy.themeTitle(themeMode))
                preferencePill(title: copy.languageTitle, value: copy.languageName(language))
            }

            HStack(spacing: 12) {
                preferencePill(title: copy.fontTitle, value: copy.fontTitle(fontStyle))
                preferencePill(title: copy.notificationsTitle, value: notificationsEnabled ? copy.done : copy.notificationsOff)
            }
        }
    }

    private var spotifyConnection: some View {
        VStack(alignment: .leading, spacing: 12) {
            ProviderConnectionStatusView(
                providerName: "Spotify",
                isConnected: isSpotifyConnected,
                providerUserId: spotifyProviderUserId
            )

            if isLoadingProviderAccounts {
                ProgressView()
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            if let providerAccountsError {
                Text(providerAccountsError)
                    .font(.footnote)
                    .foregroundStyle(.red)
            }

            Button {
                isShowingSpotifyConnect = true
            } label: {
                Label(
                    isSpotifyConnected ? "Reconnect Spotify" : "Connect Spotify",
                    systemImage: "link"
                )
                .font(.headline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private var logoutButton: some View {
        Button(action: onLogout) {
            Label("Log out", systemImage: "rectangle.portrait.and.arrow.right")
                .font(.headline.weight(.semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
        }
        .buttonStyle(.bordered)
        .foregroundStyle(theme.primaryText)
    }

    private var isSpotifyConnected: Bool {
        spotifyAccount?.connected == true
    }

    private var spotifyProviderUserId: String? {
        spotifyAccount?.providerUserId
    }

    private var spotifyAccount: ProviderAccountDTO? {
        providerAccounts.first { $0.provider == "spotify" }
    }

    @MainActor
    private func loadProviderAccounts() async {
        isLoadingProviderAccounts = true
        providerAccountsError = nil

        do {
            let response = try await APIClient.shared.fetchProviderAccounts()
            providerAccounts = response.items
            if let spotifyProviderUserId {
                UserDefaults.standard.set(
                    spotifyProviderUserId,
                    forKey: "provider.spotify.providerUserId"
                )
            } else {
                UserDefaults.standard.removeObject(forKey: "provider.spotify.providerUserId")
            }
        } catch {
            providerAccountsError = error.localizedDescription
        }

        isLoadingProviderAccounts = false
    }

    private func preferencePill(title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.caption.weight(.bold))
                .foregroundStyle(theme.tertiaryText)
            Text(value)
                .font(.headline.weight(.bold))
                .foregroundStyle(theme.primaryText)
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

    private func signalTile(value: String, title: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(value)
                .font(.headline.weight(.black))
                .foregroundStyle(theme.primaryText)
            Text(title)
                .font(.caption.weight(.bold))
                .foregroundStyle(theme.tertiaryText)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(theme.chromeStrong, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct AccountInfoCard: View {
    let rows: [(String, String)]
    let theme: Theme

    var body: some View {
        VStack(spacing: 0) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                HStack {
                    Text(row.0)
                        .foregroundStyle(theme.secondaryText)
                    Spacer()
                    Text(row.1)
                        .foregroundStyle(theme.primaryText)
                }
                .font(.subheadline.weight(.semibold))
                .padding(.vertical, 14)
                if index < rows.count - 1 {
                    Divider().overlay(theme.line)
                }
            }
        }
        .padding(.horizontal, 16)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }
}

struct AccountSettingsView: View {
    @Binding var themeMode: ThemeMode
    @Binding var language: AppLanguage
    @Binding var signedInName: String
    @Binding var signInProvider: SignInProvider
    @Binding var fontStyle: FontStyleOption
    @Binding var notificationsEnabled: Bool
    @Binding var likesNotificationsEnabled: Bool
    @Binding var savesNotificationsEnabled: Bool
    @Binding var weeklyDigestEnabled: Bool
    let theme: Theme
    let copy: Copybook
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                Section(copy.profileTitle) {
                    HStack {
                        Text(copy.displayNameTitle)
                        Spacer()
                        TextField(copy.displayNamePlaceholder, text: $signedInName)
                            .multilineTextAlignment(.trailing)
                    }

                    Picker(copy.providerTitle, selection: $signInProvider) {
                        ForEach(SignInProvider.allCases) { provider in
                            Text(copy.providerName(provider)).tag(provider)
                        }
                    }
                }

                Section(copy.appearance) {
                    Picker(copy.themeTitle, selection: $themeMode) {
                        ForEach(ThemeMode.allCases) { mode in
                            Text(copy.themeTitle(mode)).tag(mode)
                        }
                    }

                    Picker(copy.fontTitle, selection: $fontStyle) {
                        ForEach(FontStyleOption.allCases) { option in
                            Text(copy.fontTitle(option)).tag(option)
                        }
                    }
                }

                Section(copy.languageTitle) {
                    Picker(copy.languageTitle, selection: $language) {
                        ForEach(AppLanguage.allCases) { appLanguage in
                            Text(copy.languageName(appLanguage)).tag(appLanguage)
                        }
                    }
                }

                Section(copy.notificationsTitle) {
                    Toggle(copy.notificationsTitle, isOn: $notificationsEnabled)
                    Toggle(copy.likesNotificationsTitle, isOn: $likesNotificationsEnabled)
                    Toggle(copy.savesNotificationsTitle, isOn: $savesNotificationsEnabled)
                    Toggle(copy.digestNotificationsTitle, isOn: $weeklyDigestEnabled)
                }
            }
            .scrollContentBackground(.hidden)
            .background(theme.background)
            .navigationTitle(copy.settings)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(copy.done) { dismiss() }
                }
            }
        }
        .preferredColorScheme(themeMode.preferredColorScheme)
        .tint(theme.toolbarTint)
    }
}
