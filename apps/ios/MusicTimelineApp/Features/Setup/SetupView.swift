//
//  SetupView.swift
//  MusicTimelineApp
//

import SwiftUI

struct SetupView: View {
    @Binding var themeMode: ThemeMode
    @Binding var language: AppLanguage
    @Binding var signedInName: String
    @Binding var signInProvider: SignInProvider
    let theme: Theme
    let copy: Copybook
    let titleDesign: Font.Design
    let onContinue: () -> Void

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(copy.setupEyebrow)
                        .font(.caption.weight(.black))
                        .tracking(2)
                        .foregroundStyle(theme.secondaryText)

                    Text(copy.setupTitle)
                        .font(.system(size: 34, weight: .black, design: titleDesign))
                        .foregroundStyle(theme.primaryText)

                    Text(copy.setupDescription)
                        .font(.subheadline.weight(.medium))
                        .foregroundStyle(theme.secondaryText)
                }

                setupSection(title: copy.themeTitle) {
                    selectionRow(ThemeMode.allCases, current: themeMode, label: copy.themeTitle(_:))
                }

                setupSection(title: copy.languageTitle) {
                    selectionRow(AppLanguage.allCases, current: language, label: copy.languageName(_:))
                }

                setupSection(title: copy.signInTitle) {
                    VStack(alignment: .leading, spacing: 14) {
                        selectionRow(SignInProvider.allCases, current: signInProvider, label: copy.providerName(_:))

                        TextField(copy.displayNamePlaceholder, text: $signedInName)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                            .padding(.horizontal, 14)
                            .padding(.vertical, 12)
                            .background(theme.cardRaised, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                            .overlay {
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
                            }
                            .foregroundStyle(theme.primaryText)
                    }
                }

                Button {
                    if signedInName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                        signedInName = "musicfan"
                    }
                    onContinue()
                } label: {
                    Text(copy.continueTitle)
                        .font(.headline.weight(.bold))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(theme.primaryText, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
                        .foregroundStyle(theme.background)
                }
            }
            .padding(24)
        }
    }

    private func setupSection<Content: View>(title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title)
                .font(.headline.weight(.bold))
                .foregroundStyle(theme.primaryText)
            content()
        }
        .padding(18)
        .background(theme.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(theme.line, lineWidth: theme.isDark ? 1 : 1.5)
        }
    }

    private func selectionRow<Value: Identifiable & Equatable>(
        _ values: [Value],
        current: Value,
        label: @escaping (Value) -> String
    ) -> some View {
        HStack(spacing: 10) {
            ForEach(values) { value in
                Button {
                    switch value {
                    case let mode as ThemeMode:
                        themeMode = mode
                    case let appLanguage as AppLanguage:
                        language = appLanguage
                    case let provider as SignInProvider:
                        signInProvider = provider
                    default:
                        break
                    }
                } label: {
                    Text(label(value))
                        .font(.subheadline.weight(.bold))
                        .foregroundStyle(current == value ? theme.background : theme.primaryText)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 11)
                        .frame(maxWidth: .infinity)
                        .background(current == value ? theme.primaryText : theme.chromeStrong, in: Capsule())
                }
                .buttonStyle(.plain)
            }
        }
    }
}
