import Foundation

protocol StatusServicing {
    func fetchStatuses(authToken: String) async throws -> [StatusEntry]
    func createStatus(text: String, authToken: String) async throws -> StatusEntry
}

final class StatusService: StatusServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func fetchStatuses(authToken: String) async throws -> [StatusEntry] {
        let request = try URLRequest.apiRequest(endpoint: .statusFeed, method: "GET", authToken: authToken)
        return try await client.perform(request, decoding: [StatusEntry].self)
    }

    func createStatus(text: String, authToken: String) async throws -> StatusEntry {
        struct CreateStatusRequest: Codable { let statusText: String }
        let body = CreateStatusRequest(statusText: text)
        let request = try URLRequest.apiRequest(endpoint: .createStatus, method: "POST", body: body, authToken: authToken)
        return try await client.perform(request, decoding: StatusEntry.self)
    }
}
