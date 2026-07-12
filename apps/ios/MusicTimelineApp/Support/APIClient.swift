//
//  APIClient.swift
//  MusicTimelineApp
//

import Foundation

final class APIClient {
    static let shared = APIClient()

    var bearerToken: String?

    private let baseURL: URL
    private let session: URLSession

    init(
        baseURL: URL = AppEnvironment.apiBaseURL,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
        self.session = session
    }

    func fetchTimeline() async throws -> TimelineResponse {
        let request = makeRequest(path: "posts")
        let data = try await send(request)
        return try JSONDecoder().decode(TimelineResponse.self, from: data)
    }

    func searchTracks(
        provider: String,
        query: String
    ) async throws -> [TrackSearchResultDTO] {
        var components = URLComponents(
            url: baseURL.appending(path: "providers/\(provider)/search/tracks"),
            resolvingAgainstBaseURL: false
        )
        components?.queryItems = [
            URLQueryItem(name: "q", value: query)
        ]

        guard let url = components?.url else {
            throw APIClientError.invalidURL
        }

        let request = makeRequest(url: url)
        let data = try await send(request)
        return try JSONDecoder().decode([TrackSearchResultDTO].self, from: data)
    }

    func fetchPlayback(provider: String, trackId: String) async throws -> PlaybackDTO {
        let request = makeRequest(path: "providers/\(provider)/tracks/\(trackId)/playback")
        let data = try await send(request)
        return try JSONDecoder().decode(PlaybackDTO.self, from: data)
    }

    func createPost(
        provider: String,
        providerTrackId: String,
        caption: String?,
        visibility: String = "public"
    ) async throws -> PostDTO {
        var request = makeRequest(path: "posts")
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            CreatePostDTO(
                provider: provider,
                providerTrackId: providerTrackId,
                caption: caption,
                visibility: visibility
            )
        )

        let data = try await send(request)
        return try JSONDecoder().decode(PostDTO.self, from: data)
    }

    func createUser(
        displayName: String,
        handle: String,
        primaryProvider: String
    ) async throws -> UserDTO {
        var request = makeRequest(path: "users")
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            CreateUserDTO(
                displayName: displayName,
                handle: handle,
                primaryProvider: primaryProvider
            )
        )

        let data = try await send(request)
        return try JSONDecoder().decode(UserDTO.self, from: data)
    }

    func fetchMe() async throws -> UserDTO {
        let request = makeRequest(path: "me")
        let data = try await send(request)
        return try JSONDecoder().decode(UserDTO.self, from: data)
    }

    func devLogin(handle: String) async throws -> AuthTokenDTO {
        var request = makeRequest(path: "auth/dev-login")
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(DevLoginDTO(handle: handle))

        let data = try await send(request)
        return try JSONDecoder().decode(AuthTokenDTO.self, from: data)
    }

    func getSpotifyAuthorizeURL() async throws -> SpotifyAuthorizeDTO {
        let request = makeRequest(path: "auth/spotify/authorize")
        let data = try await send(request)
        return try JSONDecoder().decode(SpotifyAuthorizeDTO.self, from: data)
    }

    func connectSpotify(
        code: String,
        codeVerifier: String,
        state: String,
        expectedState: String
    ) async throws -> SpotifyConnectResponseDTO {
        var request = makeRequest(path: "auth/spotify/connect")
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            SpotifyConnectDTO(
                code: code,
                codeVerifier: codeVerifier,
                state: state,
                expectedState: expectedState
            )
        )

        let data = try await send(request)
        return try JSONDecoder().decode(SpotifyConnectResponseDTO.self, from: data)
    }

    private func makeRequest(path: String) -> URLRequest {
        makeRequest(url: baseURL.appending(path: path))
    }

    private func makeRequest(url: URL) -> URLRequest {
        var request = URLRequest(url: url)
        if let bearerToken, !bearerToken.isEmpty {
            request.setValue("Bearer \(bearerToken)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    private func send(_ request: URLRequest) async throws -> Data {
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIClientError.invalidResponse
        }

        guard (200..<300).contains(httpResponse.statusCode) else {
            throw APIClientError.httpStatus(
                httpResponse.statusCode,
                errorMessage(from: data)
            )
        }

        return data
    }

    private func errorMessage(from data: Data) -> String? {
        if let errorResponse = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
            if let detail = errorResponse.detail, !detail.isEmpty {
                return detail
            }
        }

        if let validationError = try? JSONDecoder().decode(APIValidationErrorResponse.self, from: data),
           !validationError.detail.isEmpty {
            return validationError.detail.first?.msg ?? "Request validation failed."
        }

        return String(data: data, encoding: .utf8)
    }
}

private struct APIErrorResponse: Decodable {
    let detail: String?
}

private struct APIValidationErrorResponse: Decodable {
    let detail: [APIValidationErrorDetail]
}

private struct APIValidationErrorDetail: Decodable {
    let msg: String?
}

enum APIClientError: LocalizedError {
    case invalidURL
    case invalidResponse
    case httpStatus(Int, String?)

    var statusCode: Int? {
        switch self {
        case .invalidURL, .invalidResponse:
            return nil
        case .httpStatus(let statusCode, _):
            return statusCode
        }
    }

    var isProviderConnectionRequired: Bool {
        switch self {
        case .invalidURL, .invalidResponse:
            return false
        case .httpStatus(let statusCode, let message):
            return statusCode == 409
                && message?.localizedCaseInsensitiveContains("Provider account is not connected") == true
        }
    }

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid API URL."
        case .invalidResponse:
            return "Invalid API response."
        case .httpStatus(let statusCode, let message):
            if statusCode == 401 {
                return "Authentication is required. Set a bearer token before using this API."
            }
            if self.isProviderConnectionRequired {
                return "Provider account is not connected."
            }
            if let message, !message.isEmpty {
                return "API request failed with status \(statusCode): \(message)"
            }
            return "API request failed with status \(statusCode)."
        }
    }
}
