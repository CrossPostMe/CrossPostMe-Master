import Foundation

@MainActor
final class HealthAnalyticsViewModel: ObservableObject {
    @Published private(set) var history: [HealthHistoryPoint] = []
    @Published private(set) var incidents: [HealthIncident] = []
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?

    private let service: HealthServicing
    var authToken: String?

    init(service: HealthServicing = HealthService()) {
        self.service = service
    }

    func refresh() async {
        guard authToken != nil else { return }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            async let historyTask = service.fetchHistory(authToken: authToken)
            async let incidentsTask = service.fetchIncidents(authToken: authToken)
            var fetchedHistory = try await historyTask
            let fetchedIncidents = try await incidentsTask
            fetchedHistory.sort { $0.timestamp < $1.timestamp }
            history = fetchedHistory
            incidents = fetchedIncidents.sorted { $0.startedAt > $1.startedAt }
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    var uptimePercentage: Double {
        guard !history.isEmpty else { return 100 }
        let healthy = history.filter { $0.status.lowercased() == "ok" || $0.status.lowercased() == "healthy" }.count
        return (Double(healthy) / Double(history.count)) * 100
    }

    var averageLatency: Double? {
        guard !history.isEmpty else { return nil }
        let total = history.reduce(0.0) { $0 + $1.latencyMs }
        return total / Double(history.count)
    }

    var recentHistory: [HealthHistoryPoint] {
        history.suffix(48)
    }
}