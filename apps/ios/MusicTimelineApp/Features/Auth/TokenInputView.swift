//
//  TokenInputView.swift
//  MusicTimelineApp
//

import SwiftUI

struct TokenInputView: View {
    @EnvironmentObject private var authSession: AuthSession
    @Environment(\.dismiss) private var dismiss

    @State private var token = ""
    @State private var isVerifying = false

    var body: some View {
        Form {
            Section("JWT") {
                TextField("Paste backend JWT", text: $token, axis: .vertical)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .lineLimit(4...8)
            }

            Section {
                Button {
                    Task {
                        await verifyAndSave()
                    }
                } label: {
                    if isVerifying {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                    } else {
                        Text("Save and Continue")
                            .frame(maxWidth: .infinity)
                    }
                }
                .disabled(isVerifying || trimmedToken.isEmpty)
            }

            if let user = authSession.currentUser {
                Section("Signed in") {
                    Text(user.displayName)
                    Text("@\(user.handle)")
                        .foregroundStyle(.secondary)
                }
            }

            if let message = authSession.authErrorMessage {
                Section {
                    Text(message)
                        .font(.subheadline)
                        .foregroundStyle(.red)
                }
            }
        }
        .navigationTitle("Enter JWT")
        .onAppear {
            token = authSession.savedToken ?? ""
        }
    }

    @MainActor
    private func verifyAndSave() async {
        isVerifying = true
        await authSession.signIn(with: trimmedToken)
        isVerifying = false

        if authSession.isAuthenticated {
            dismiss()
        }
    }

    private var trimmedToken: String {
        token.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

#Preview("Token Input") {
    NavigationStack {
        TokenInputView()
            .environmentObject(
                AuthSession(
                    apiClient: APIClient(),
                    tokenStore: InMemoryAuthTokenStore(),
                    legacyDefaults: UserDefaults(suiteName: "MusicTimelineApp.preview") ?? .standard
                )
            )
    }
}
