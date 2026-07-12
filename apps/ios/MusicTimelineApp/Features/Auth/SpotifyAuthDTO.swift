//
//  SpotifyAuthDTO.swift
//  MusicTimelineApp
//

import Foundation

struct SpotifyAuthorizeDTO: Decodable {
    let authorizationUrl: String
    let state: String
    let codeVerifier: String

    enum CodingKeys: String, CodingKey {
        case authorizationUrl = "authorization_url"
        case state
        case codeVerifier = "code_verifier"
    }
}

struct SpotifyConnectDTO: Encodable {
    let code: String
    let codeVerifier: String
    let state: String
    let expectedState: String

    enum CodingKeys: String, CodingKey {
        case code
        case codeVerifier = "code_verifier"
        case state
        case expectedState = "expected_state"
    }
}

struct SpotifyConnectResponseDTO: Decodable {
    let provider: String
    let providerUserId: String

    enum CodingKeys: String, CodingKey {
        case provider
        case providerUserId = "provider_user_id"
    }
}
