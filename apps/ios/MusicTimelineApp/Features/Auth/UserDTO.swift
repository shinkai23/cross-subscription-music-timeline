//
//  UserDTO.swift
//  MusicTimelineApp
//

import Foundation

struct UserDTO: Decodable, Identifiable {
    let id: String
    let displayName: String
    let handle: String
    let primaryProvider: String?
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case handle
        case primaryProvider = "primary_provider"
        case createdAt = "created_at"
    }
}

typealias CurrentUserDTO = UserDTO

struct ProviderAccountsResponseDTO: Decodable {
    let items: [ProviderAccountDTO]
}

struct ProviderAccountDTO: Decodable, Identifiable {
    var id: String {
        provider
    }

    let provider: String
    let providerUserId: String
    let connected: Bool
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case provider
        case providerUserId = "provider_user_id"
        case connected
        case createdAt = "created_at"
    }
}

struct CreateUserDTO: Encodable {
    let displayName: String
    let handle: String
    let primaryProvider: String?

    enum CodingKeys: String, CodingKey {
        case displayName = "display_name"
        case handle
        case primaryProvider = "primary_provider"
    }
}
