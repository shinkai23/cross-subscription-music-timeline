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
    private let defaults: UserDefaults
    private let tokenKey = "auth.bearerToken"

    convenience init(defaults: UserDefaults = .standard) {
        self.init(apiClient: .shared, defaults: defaults)
    }

    init(
        apiClient: APIClient,
        defaults: UserDefaults = .standard
    ) {
        self.apiClient = apiClient
        self.defaults = defaults
        apiClient.bearerToken = savedToken
    }

    var isAuthenticated: Bool {
        currentUser != nil
    }

    var savedToken: String? {
        defaults.string(forKey: tokenKey)
    }

    func restore() async {
        guard let token = savedToken, !token.isEmpty else {
            apiClient.bearerToken = nil
            isRestoring = false
            return
        }

        await signIn(with: token, persistToken: false)
        if !isAuthenticated {
            defaults.removeObject(forKey: tokenKey)
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
                defaults.set(trimmedToken, forKey: tokenKey)
            }
        } catch {
            currentUser = nil
            apiClient.bearerToken = nil
            if persistToken {
                defaults.removeObject(forKey: tokenKey)
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
        defaults.removeObject(forKey: tokenKey)
    }
}

extension AuthSession {
    static func previewAuthenticated() -> AuthSession {
        let session = AuthSession(
            apiClient: APIClient(),
            defaults: previewDefaults()
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
            defaults: previewDefaults()
        )
        session.currentUser = nil
        session.isRestoring = false
        return session
    }

    private static func previewDefaults() -> UserDefaults {
        UserDefaults(suiteName: "MusicTimelineApp.preview") ?? .standard
    }
}
