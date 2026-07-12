//
//  AppEnvironment.swift
//  MusicTimelineApp
//

import Foundation

enum AppEnvironment {
    static var apiBaseURL: URL {
        if let overrideURL = apiBaseURLOverride {
            return overrideURL
        }

        #if targetEnvironment(simulator)
        return simulatorAPIBaseURL
        #else
        return physicalDeviceAPIBaseURL
        #endif
    }

    static let simulatorAPIBaseURL = URL(string: "http://localhost:4000")!
    static let physicalDeviceAPIBaseURL = URL(string: "http://192.168.0.12:4000")!

    private static var apiBaseURLOverride: URL? {
        guard
            let value = ProcessInfo.processInfo.environment["API_BASE_URL"],
            !value.isEmpty
        else {
            return nil
        }

        return URL(string: value)
    }
}
