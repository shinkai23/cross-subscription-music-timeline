//
//  MusicTimelineAppApp.swift
//  MusicTimelineApp
//
//  Created by Sinkai I on 2026/05/06.
//

import SwiftUI
import SwiftData

@main
struct MusicTimelineAppApp: App {
    @StateObject private var authSession = AuthSession()

    var sharedModelContainer: ModelContainer = {
        let schema = Schema([
            Item.self,
        ])
        let modelConfiguration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)

        do {
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authSession)
                .task {
                    await authSession.restore()
                }
        }
        .modelContainer(sharedModelContainer)
    }
}
