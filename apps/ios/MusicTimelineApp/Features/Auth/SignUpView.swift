//
//  SignUpView.swift
//  MusicTimelineApp
//

import SwiftUI

struct SignUpView: View {
    var apiClient: APIClient = .shared
    let onCreated: () -> Void

    @EnvironmentObject private var authSession: AuthSession
    @State private var displayName = ""
    @State private var handle = ""
    @State private var primaryProvider = SearchProvider.spotify
    @State private var createdUser: UserDTO?
    @State private var isCreating = false
    @State private var errorMessage: String?

    var body: some View {
        Form {
            Section("User") {
                TextField("Display name", text: $displayName)
                    .textInputAutocapitalization(.words)
                TextField("Handle", text: $handle)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                Picker("Primary provider", selection: $primaryProvider) {
                    ForEach(SearchProvider.allCases) { provider in
                        Text(provider.displayName).tag(provider)
                    }
                }
            }

            if let createdUser {
                Section("Created") {
                    Text(createdUser.displayName)
                    Text("@\(createdUser.handle)")
                        .foregroundStyle(.secondary)
                    Button("Continue to Handle Login") {
                        onCreated()
                    }
                }
            }

            if let errorMessage {
                Section {
                    Text(errorMessage)
                        .font(.subheadline)
                        .foregroundStyle(.red)
                }
            }

            if let message = authSession.authErrorMessage {
                Section {
                    Text(message)
                        .font(.subheadline)
                        .foregroundStyle(.red)
                }
            }

            Section {
                Button {
                    Task {
                        await createUser()
                    }
                } label: {
                    if isCreating {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Create User")
                            .frame(maxWidth: .infinity)
                    }
                }
                .disabled(isCreating || trimmedDisplayName.isEmpty || trimmedHandle.isEmpty)
            }
        }
        .navigationTitle("Create User")
    }

    @MainActor
    private func createUser() async {
        guard !isCreating else { return }
        isCreating = true
        errorMessage = nil

        do {
            let user = try await apiClient.createUser(
                displayName: trimmedDisplayName,
                handle: trimmedHandle,
                primaryProvider: primaryProvider.rawValue
            )
            createdUser = user
            await authSession.devLogin(handle: user.handle)
        } catch {
            errorMessage = error.localizedDescription
        }

        isCreating = false
    }

    private var trimmedDisplayName: String {
        displayName.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private var trimmedHandle: String {
        handle.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

#Preview("Sign Up") {
    NavigationStack {
        SignUpView {}
            .environmentObject(AuthSession())
    }
}
