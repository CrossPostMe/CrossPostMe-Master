import Foundation

struct HealthStatus: Codable, Equatable {
    let endpoint: String
    let status: String
    let checkedAt: Date
}

protocol HealthServicing {
    func fetchHealth(authToken: String?) async throws -> HealthStatus
    func fetchReadiness(authToken: String?) async throws -> HealthStatus
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

struct Incident: Codable {
    let id: String
    let description: String
    let date: Date
}

protocol IncidentServicing {
    func fetchIncidents(authToken: String?) async throws -> [Incident]
}

final class IncidentService: IncidentServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func fetchIncidents(authToken: String?) async throws -> [Incident] {
        let request = try URLRequest.apiRequest(endpoint: .incidents,
                                                method: "GET",
                                                authToken: authToken)
        let response = try await client.perform(request, decoding: [Incident].self)
        return response
    }
}
