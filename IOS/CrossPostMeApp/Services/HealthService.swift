import Foundation

struct HealthStatus: Codable, Equatable {
    let endpoint: String
    let status: String
    let checkedAt: Date
}

struct HealthHistoryPoint: Codable, Identifiable {
    let timestamp: Date
    let status: String
    let latencyMs: Double

    var id: Date { timestamp }

    enum CodingKeys: String, CodingKey {
        case timestamp
        case status
        case latencyMs = "latency_ms"
    }
}

struct HealthIncident: Codable, Identifiable {
    let id: UUID
    let title: String
    let details: String
    let startedAt: Date
    let resolvedAt: Date?
    let severity: String

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case details
        case startedAt = "started_at"
        case resolvedAt = "resolved_at"
        case severity
    }
}

protocol HealthServicing {
    func fetchHealth(authToken: String?) async throws -> HealthStatus
    func fetchReadiness(authToken: String?) async throws -> HealthStatus
    func fetchHistory(authToken: String?) async throws -> [HealthHistoryPoint]
    func fetchIncidents(authToken: String?) async throws -> [HealthIncident]
}

final class HealthService: HealthServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func fetchHealth(authToken: String?) async throws -> HealthStatus {
        try await check(.health, authToken: authToken)
    }

    func fetchReadiness(authToken: String?) async throws -> HealthStatus {
        try await check(.readiness, authToken: authToken)
    }

    func fetchHistory(authToken: String?) async throws -> [HealthHistoryPoint] {
        let request = try URLRequest.apiRequest(endpoint: .healthHistory,
                                                method: "GET",
                                                authToken: authToken)
        return try await client.perform(request, decoding: [HealthHistoryPoint].self)
    }

    func fetchIncidents(authToken: String?) async throws -> [HealthIncident] {
        let request = try URLRequest.apiRequest(endpoint: .healthIncidents,
                                                method: "GET",
                                                authToken: authToken)
        return try await client.perform(request, decoding: [HealthIncident].self)
    }

    private func check(_ endpoint: APIEndpoint, authToken: String?) async throws -> HealthStatus {
        let request = try URLRequest.apiRequest(endpoint: endpoint,
                                                method: "GET",
                                                authToken: authToken)
        struct WireStatus: Codable {
            let status: String
        }
        let response = try await client.perform(request, decoding: WireStatus.self)
        return HealthStatus(endpoint: endpoint.path,
                             status: response.status,
                             checkedAt: Date())
    }
}
