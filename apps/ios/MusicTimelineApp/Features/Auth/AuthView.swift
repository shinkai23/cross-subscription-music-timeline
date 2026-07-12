//
//  AuthView.swift
//  MusicTimelineApp
//

import SwiftUI

struct AuthView: View {
    @EnvironmentObject private var authSession: AuthSession
    @State private var isShowingLogin = false
    @State private var isShowingSignUp = false
    @State private var isShowingTokenInput = false

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 18) {
                Spacer()

                VStack(alignment: .leading, spacing: 8) {
                    Text("Music Timeline")
                        .font(.system(size: 34, weight: .black))
                    Text("Log in with a development handle, or create a user first.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                VStack(spacing: 12) {
                    Button {
                        isShowingLogin = true
                    } label: {
                        Label("Log In with Handle", systemImage: "person.crop.circle.badge.checkmark")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)

                    Button {
                        isShowingSignUp = true
                    } label: {
                        Label("Create User", systemImage: "person.badge.plus")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Button {
                        isShowingTokenInput = true
                    } label: {
                        Label("Enter JWT", systemImage: "key")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }

                if let message = authSession.authErrorMessage {
                    Text(message)
                        .font(.footnote)
                        .foregroundStyle(.red)
                        .fixedSize(horizontal: false, vertical: true)
                }

                Spacer()
            }
            .padding(24)
            .navigationDestination(isPresented: $isShowingLogin) {
                LoginView()
            }
            .navigationDestination(isPresented: $isShowingSignUp) {
                SignUpView {
                    isShowingSignUp = false
                    isShowingLogin = true
                }
            }
            .navigationDestination(isPresented: $isShowingTokenInput) {
                TokenInputView()
            }
        }
    }
}

#Preview("Auth") {
    AuthView()
        .environmentObject(
            AuthSession(
                apiClient: APIClient(),
                tokenStore: InMemoryAuthTokenStore(),
                legacyDefaults: UserDefaults(suiteName: "MusicTimelineApp.preview") ?? .standard
            )
        )
}
