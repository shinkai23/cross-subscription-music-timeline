//
//  SpotifyConnectView.swift
//  MusicTimelineApp
//

import SwiftUI

#if canImport(UIKit)
import UIKit
#endif

struct SpotifyConnectView: View {
    var apiClient: APIClient = .shared
    let onConnected: (SpotifyConnectResponseDTO) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var authorization: SpotifyAuthorizeDTO?
    @State private var callbackURL = ""
    @State private var code = ""
    @State private var state = ""
    @State private var connectedResponse: SpotifyConnectResponseDTO?
    @State private var isLoadingAuthorization = false
    @State private var isConnecting = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    ProviderConnectionStatusView(
                        providerName: "Spotify",
                        isConnected: connectedResponse != nil,
                        providerUserId: connectedResponse?.providerUserId
                    )
                }

                Section("Authorize") {
                    Button {
                        Task {
                            await startAuthorization()
                        }
                    } label: {
                        if isLoadingAuthorization {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("Open Spotify Authorization")
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(isLoadingAuthorization || isConnecting)

                    if let authorization {
                        Text("Expected state: \(authorization.state)")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                if authorization != nil {
                    Section("Callback") {
                        TextField("Paste callback URL", text: $callbackURL, axis: .vertical)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .lineLimit(2...5)
                            .onChange(of: callbackURL) {
                                parseCallbackURL()
                            }

                        TextField("code", text: $code)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()

                        TextField("state", text: $state)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                    }

                    Section {
                        Button {
                            Task {
                                await connect()
                            }
                        } label: {
                            if isConnecting {
                                ProgressView()
                                    .frame(maxWidth: .infinity)
                            } else {
                                Text("Connect Spotify")
                                    .frame(maxWidth: .infinity)
                            }
                        }
                        .disabled(isConnecting || code.isEmpty || state.isEmpty)
                    }
                }

                if let errorMessage {
                    Section {
                        Text(errorMessage)
                            .font(.subheadline)
                            .foregroundStyle(.red)
                    }
                }

                if connectedResponse != nil {
                    Section {
                        Button("Done") {
                            dismiss()
                        }
                    }
                }
            }
            .navigationTitle("Connect Spotify")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Close") {
                        dismiss()
                    }
                }
            }
        }
    }

    @MainActor
    private func startAuthorization() async {
        isLoadingAuthorization = true
        errorMessage = nil

        do {
            let authorization = try await apiClient.getSpotifyAuthorizeURL()
            self.authorization = authorization
            openAuthorizationURL(authorization.authorizationUrl)
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoadingAuthorization = false
    }

    @MainActor
    private func connect() async {
        guard let authorization else { return }
        isConnecting = true
        errorMessage = nil

        do {
            let response = try await apiClient.connectSpotify(
                code: code.trimmingCharacters(in: .whitespacesAndNewlines),
                codeVerifier: authorization.codeVerifier,
                state: state.trimmingCharacters(in: .whitespacesAndNewlines),
                expectedState: authorization.state
            )
            connectedResponse = response
            onConnected(response)
        } catch {
            errorMessage = error.localizedDescription
        }

        isConnecting = false
    }

    private func parseCallbackURL() {
        guard
            let components = URLComponents(string: callbackURL),
            let queryItems = components.queryItems
        else {
            return
        }

        if let parsedCode = queryItems.first(where: { $0.name == "code" })?.value {
            code = parsedCode
        }

        if let parsedState = queryItems.first(where: { $0.name == "state" })?.value {
            state = parsedState
        }
    }

    private func openAuthorizationURL(_ value: String) {
        guard let url = URL(string: value) else {
            errorMessage = "Invalid Spotify authorization URL."
            return
        }

        #if canImport(UIKit)
        UIApplication.shared.open(url)
        #endif
    }
}

#Preview("Spotify Connect") {
    SpotifyConnectView { _ in }
}
