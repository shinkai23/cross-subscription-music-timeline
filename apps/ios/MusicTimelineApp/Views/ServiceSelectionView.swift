import SwiftUI

struct ServiceSelectionView: View {
    @Binding var selectedProvider: MusicProvider?
    @StateObject private var appleMusicAuthorization = AppleMusicAuthorizationService()

    var body: some View {
        NavigationStack {
            List {
                Section("Primary service") {
                    ForEach(MusicProvider.allCases) { provider in
                        Button {
                            selectedProvider = provider
                        } label: {
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(provider.displayName)
                                    Text(provider == .appleMusic ? "Best supported in the iOS prototype" : "OAuth PKCE integration planned")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }

                                Spacer()

                                if selectedProvider == provider {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundStyle(.tint)
                                }
                            }
                        }
                    }
                }

                Section("Apple Music") {
                    HStack {
                        Text("Authorization")
                        Spacer()
                        Text(String(describing: appleMusicAuthorization.status))
                            .foregroundStyle(.secondary)
                    }

                    Button("Connect Apple Music") {
                        Task {
                            await appleMusicAuthorization.requestAuthorization()
                        }
                    }
                }
            }
            .navigationTitle("Services")
        }
    }
}

#Preview {
    ServiceSelectionView(selectedProvider: .constant(.appleMusic))
}

