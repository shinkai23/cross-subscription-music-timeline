//
//  LoginView.swift
//  MusicTimelineApp
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var authSession: AuthSession
    @Environment(\.dismiss) private var dismiss

    @State private var handle = ""
    @State private var isLoggingIn = false

    var body: some View {
        Form {
            Section("Handle") {
                TextField("sinkaii", text: $handle)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .submitLabel(.go)
                    .onSubmit {
                        Task {
                            await login()
                        }
                    }
            }

            Section {
                Button {
                    Task {
                        await login()
                    }
                } label: {
                    if isLoggingIn {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Log In")
                            .frame(maxWidth: .infinity)
                    }
                }
                .disabled(isLoggingIn || trimmedHandle.isEmpty)
            }

            if let message = authSession.authErrorMessage {
                Section {
                    Text(message)
                        .font(.subheadline)
                        .foregroundStyle(.red)
                }
            }
        }
        .navigationTitle("Dev Login")
    }

    @MainActor
    private func login() async {
        guard !isLoggingIn else { return }
        isLoggingIn = true
        await authSession.devLogin(handle: trimmedHandle)
        isLoggingIn = false

        if authSession.isAuthenticated {
            dismiss()
        }
    }

    private var trimmedHandle: String {
        handle.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

#Preview("Dev Login") {
    NavigationStack {
        LoginView()
            .environmentObject(
                AuthSession(
                    apiClient: APIClient(),
                    tokenStore: InMemoryAuthTokenStore(),
                    legacyDefaults: UserDefaults(suiteName: "MusicTimelineApp.preview") ?? .standard
                )
            )
    }
}
