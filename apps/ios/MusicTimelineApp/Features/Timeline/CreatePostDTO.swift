//
//  CreatePostDTO.swift
//  MusicTimelineApp
//

import Foundation

struct CreatePostDTO: Encodable {
    let provider: String
    let providerTrackId: String
    let caption: String?
    let visibility: String

    enum CodingKeys: String, CodingKey {
        case provider
        case providerTrackId = "provider_track_id"
        case caption
        case visibility
    }
}
