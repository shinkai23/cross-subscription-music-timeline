//
//  AuthTokenStore.swift
//  MusicTimelineApp
//

import Foundation
import Security

protocol AuthTokenStore {
    func readToken() -> String?
    func saveToken(_ token: String) throws
    func deleteToken()
}

enum AuthTokenStoreError: LocalizedError {
    case saveFailed(OSStatus)

    var errorDescription: String? {
        switch self {
        case .saveFailed(let status):
            return "Failed to save JWT in Keychain. OSStatus: \(status)"
        }
    }
}

final class KeychainAuthTokenStore: AuthTokenStore {
    private let service = "MusicTimelineApp.auth"
    private let account = "bearerToken"

    func readToken() -> String? {
        var query = baseQuery()
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)

        guard status == errSecSuccess,
              let data = item as? Data,
              let token = String(data: data, encoding: .utf8)
        else {
            return nil
        }

        return token
    }

    func saveToken(_ token: String) throws {
        deleteToken()

        var query = baseQuery()
        query[kSecValueData as String] = Data(token.utf8)
        query[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw AuthTokenStoreError.saveFailed(status)
        }
    }

    func deleteToken() {
        SecItemDelete(baseQuery() as CFDictionary)
    }

    private func baseQuery() -> [String: Any] {
        [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
    }
}

final class InMemoryAuthTokenStore: AuthTokenStore {
    private var token: String?

    init(token: String? = nil) {
        self.token = token
    }

    func readToken() -> String? {
        token
    }

    func saveToken(_ token: String) throws {
        self.token = token
    }

    func deleteToken() {
        token = nil
    }
}
