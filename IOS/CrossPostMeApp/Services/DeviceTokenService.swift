import Foundation

protocol DeviceTokenServicing {
    func registerDeviceToken(_ token: String, platform: String, authToken: String?) async throws
}

struct DeviceTokenRequest: Codable {
    let token: String
    let platform: String
}

final class DeviceTokenService: DeviceTokenServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func registerDeviceToken(_ token: String, platform: String = "ios", authToken: String?) async throws {
        let body = DeviceTokenRequest(token: token, platform: platform)
        let request = try URLRequest.apiRequest(endpoint: .registerDeviceToken,
                                                method: "POST",
                                                body: body,
                                                authToken: authToken)
        try await client.perform(request)
    }
}
