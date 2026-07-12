//
//  AuthSession.swift
//  MusicTimelineApp
//

import Foundation
import Combine

@MainActor
final class AuthSession: ObservableObject {
    @Published private(set) var currentUser: CurrentUserDTO?
    @Published private(set) var isRestoring = true
    @Published var authErrorMessage: String?

    private let apiClient: APIClient
    private let tokenStore: AuthTokenStore
    private let legacyDefaults: UserDefaults
    private let legacyTokenKey = "auth.bearerToken"

    convenience init() {
        self.init(apiClient: .shared, tokenStore: KeychainAuthTokenStore())
    }

    init(
        apiClient: APIClient,
        tokenStore: AuthTokenStore,
        legacyDefaults: UserDefaults = .standard
    ) {
        self.apiClient = apiClient
        self.tokenStore = tokenStore
        self.legacyDefaults = legacyDefaults
        apiClient.bearerToken = savedToken
    }

    var isAuthenticated: Bool {
        currentUser != nil
    }

    var savedToken: String? {
        tokenStore.readToken() ?? legacyDefaults.string(forKey: legacyTokenKey)
    }

    func restore() async {
        guard let token = migrateLegacyTokenIfNeeded(), !token.isEmpty else {
            apiClient.bearerToken = nil
            isRestoring = false
            return
        }

        await signIn(with: token, persistToken: false)
        if !isAuthenticated {
            tokenStore.deleteToken()
            legacyDefaults.removeObject(forKey: legacyTokenKey)
        }
        isRestoring = false
    }

    func signIn(with token: String, persistToken: Bool = true) async {
        let trimmedToken = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedToken.isEmpty else {
            authErrorMessage = "JWT is required."
            currentUser = nil
            return
        }

        apiClient.bearerToken = trimmedToken
        authErrorMessage = nil

        do {
            let user = try await apiClient.fetchMe()
            currentUser = user
            if persistToken {
                do {
                    try tokenStore.saveToken(trimmedToken)
                    legacyDefaults.removeObject(forKey: legacyTokenKey)
                } catch {
                    authErrorMessage = error.localizedDescription
                }
            }
        } catch {
            currentUser = nil
            apiClient.bearerToken = nil
            if persistToken {
                tokenStore.deleteToken()
                legacyDefaults.removeObject(forKey: legacyTokenKey)
            }
            authErrorMessage = error.localizedDescription
        }
    }

    func devLogin(handle: String) async {
        let trimmedHandle = handle.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedHandle.isEmpty else {
            authErrorMessage = "Handle is required."
            currentUser = nil
            return
        }

        authErrorMessage = nil

        do {
            let token = try await apiClient.devLogin(handle: trimmedHandle)
            await signIn(with: token.accessToken)
        } catch {
            currentUser = nil
            apiClient.bearerToken = nil
            authErrorMessage = error.localizedDescription
        }
    }

    func logout() {
        currentUser = nil
        authErrorMessage = nil
        apiClient.bearerToken = nil
        tokenStore.deleteToken()
        legacyDefaults.removeObject(forKey: legacyTokenKey)
    }

    private func migrateLegacyTokenIfNeeded() -> String? {
        if let keychainToken = tokenStore.readToken(), !keychainToken.isEmpty {
            return keychainToken
        }

        guard let legacyToken = legacyDefaults.string(forKey: legacyTokenKey),
              !legacyToken.isEmpty
        else {
            return nil
        }

        do {
            try tokenStore.saveToken(legacyToken)
            legacyDefaults.removeObject(forKey: legacyTokenKey)
        } catch {
            authErrorMessage = error.localizedDescription
        }

        return legacyToken
    }
}

extension AuthSession {
    static func previewAuthenticated() -> AuthSession {
        let session = AuthSession(
            apiClient: APIClient(),
            tokenStore: InMemoryAuthTokenStore(),
            legacyDefaults: previewDefaults()
        )
        session.currentUser = UserDTO(
            id: "preview-user",
            displayName: "Sinkai",
            handle: "sinkaii",
            primaryProvider: "spotify",
            createdAt: "2026-07-11T00:00:00Z"
        )
        session.isRestoring = false
        return session
    }

    static func previewUnauthenticated() -> AuthSession {
        let session = AuthSession(
            apiClient: APIClient(),
            tokenStore: InMemoryAuthTokenStore(),
            legacyDefaults: previewDefaults()
        )
        session.currentUser = nil
        session.isRestoring = false
        return session
    }

    private static func previewDefaults() -> UserDefaults {
        UserDefaults(suiteName: "MusicTimelineApp.preview") ?? .standard
    }
}
