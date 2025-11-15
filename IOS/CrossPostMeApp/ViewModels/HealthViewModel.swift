import Foundation
import SwiftUI

@MainActor
final class HealthViewModel: ObservableObject {
    @Published private(set) var healthStatus: HealthStatus?
    @Published private(set) var readinessStatus: HealthStatus?
    @Published private(set) var isLoading = false
    @Published var errorMessage: String?

    private let service: HealthServicing
    var authToken: String?

    init(service: HealthServicing = HealthService()) {
        self.service = service
    }

    func refresh() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            async let health = service.fetchHealth(authToken: authToken)
            async let ready = service.fetchReadiness(authToken: authToken)
            healthStatus = try await health
            readinessStatus = try await ready
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }
}
