//
//  AuthTokenDTO.swift
//  MusicTimelineApp
//

import Foundation

struct AuthTokenDTO: Decodable {
    let accessToken: String
    let tokenType: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case tokenType = "token_type"
    }
}

struct DevLoginDTO: Encodable {
    let handle: String
}
