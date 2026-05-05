import SwiftUI

struct ReportSheetView: View {
    enum Reason: String, CaseIterable, Identifiable {
        case copyright = "Copyright"
        case misleading = "Misleading metadata"
        case spam = "Spam"
        case abuse = "Abuse"

        var id: String { rawValue }
    }

    @Environment(\.dismiss) private var dismiss
    @State private var selectedReason: Reason = .copyright
    @State private var details = ""

    var body: some View {
        NavigationStack {
            Form {
                Picker("Reason", selection: $selectedReason) {
                    ForEach(Reason.allCases) { reason in
                        Text(reason.rawValue).tag(reason)
                    }
                }

                TextEditor(text: $details)
                    .frame(minHeight: 140)
            }
            .navigationTitle("Report")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Submit") {
                        // TODO: Submit moderation report.
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    ReportSheetView()
}

