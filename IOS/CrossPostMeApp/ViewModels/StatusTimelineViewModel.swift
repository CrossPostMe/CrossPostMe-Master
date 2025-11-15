import Foundation
import SwiftUI

@MainActor
final class StatusTimelineViewModel: ObservableObject {
    @Published private(set) var statuses: [StatusEntry] = []
    @Published var isLoading = false
    @Published var composerText: String = ""
    @Published var errorMessage: String?

    var authToken: String? {
        didSet {
            guard authToken != oldValue else { return }
            Task { await reloadIfPossible() }
        }
    }

    private let service: StatusServicing

    init(service: StatusServicing = StatusService()) {
        self.service = service
    }

    func reloadIfPossible() async {
        guard let token = authToken else {
            statuses = []
            return
        }
        await fetchStatuses(token: token)
    }

    func fetchStatuses(token: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            statuses = try await service.fetchStatuses(authToken: token)
            NotificationManager.shared.recordLatestStatus(statuses.first?.id)
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    func submitStatus(token: String) async {
        let trimmed = composerText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        errorMessage = nil
        do {
            let created = try await service.createStatus(text: trimmed, authToken: token)
            statuses.insert(created, at: 0)
            NotificationManager.shared.recordLatestStatus(created.id)
            composerText = ""
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }
}
