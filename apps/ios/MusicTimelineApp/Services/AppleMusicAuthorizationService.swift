import Foundation
import MusicKit

@MainActor
final class AppleMusicAuthorizationService: ObservableObject {
    @Published private(set) var status: MusicAuthorization.Status = MusicAuthorization.currentStatus
    @Published private(set) var subscription: MusicSubscription?

    func requestAuthorization() async {
        status = await MusicAuthorization.request()
        await refreshSubscription()
    }

    func refreshSubscription() async {
        do {
            subscription = try await MusicSubscription.current
        } catch {
            subscription = nil
        }
    }
}

