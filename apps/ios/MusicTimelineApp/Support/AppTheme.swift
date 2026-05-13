//
//  AppTheme.swift
//  MusicTimelineApp
//

import SwiftUI

struct Theme {
    let isDark: Bool
    let background: Color
    let card: Color
    let cardRaised: Color
    let line: Color
    let primaryText: Color
    let secondaryText: Color
    let tertiaryText: Color
    let chrome: Color
    let chromeStrong: Color
    let toolbarTint: Color
    let serviceDefault: Color
    let shadow: Color

    let spotify: Color
    let appleMusic: Color
    let youTubeMusic: Color

    static let dark = Theme(
        isDark: true,
        background: .black,
        card: Color(red: 0.08, green: 0.08, blue: 0.10),
        cardRaised: Color(red: 0.12, green: 0.12, blue: 0.15),
        line: Color.white.opacity(0.08),
        primaryText: .white,
        secondaryText: Color.white.opacity(0.66),
        tertiaryText: Color.white.opacity(0.46),
        chrome: Color.white.opacity(0.06),
        chromeStrong: Color.white.opacity(0.14),
        toolbarTint: .white,
        serviceDefault: .white,
        shadow: .black.opacity(0.35),
        spotify: Color(red: 0.12, green: 0.84, blue: 0.38),
        appleMusic: Color(red: 1.00, green: 0.23, blue: 0.45),
        youTubeMusic: Color(red: 1.00, green: 0.29, blue: 0.24)
    )

    static let light = Theme(
        isDark: false,
        background: Color(red: 0.92, green: 0.93, blue: 0.95),
        card: Color(red: 0.99, green: 0.99, blue: 0.98),
        cardRaised: Color(red: 0.89, green: 0.90, blue: 0.93),
        line: Color.black.opacity(0.14),
        primaryText: Color(red: 0.08, green: 0.08, blue: 0.10),
        secondaryText: Color.black.opacity(0.68),
        tertiaryText: Color.black.opacity(0.46),
        chrome: Color.black.opacity(0.07),
        chromeStrong: Color.black.opacity(0.14),
        toolbarTint: .black,
        serviceDefault: .black,
        shadow: .black.opacity(0.10),
        spotify: Color(red: 0.10, green: 0.67, blue: 0.30),
        appleMusic: Color(red: 0.92, green: 0.20, blue: 0.40),
        youTubeMusic: Color(red: 0.92, green: 0.26, blue: 0.18)
    )
}
