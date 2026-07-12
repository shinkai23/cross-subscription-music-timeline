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
