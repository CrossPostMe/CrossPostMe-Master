import Foundation

protocol AuthServicing {
    func register(request: RegisterRequest) async throws -> AuthResponse
    func login(request: LoginRequest) async throws -> AuthResponse
}

final class AuthService: AuthServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func register(request: RegisterRequest) async throws -> AuthResponse {
        let urlRequest = try URLRequest.apiRequest(endpoint: .register, method: "POST", body: request)
        return try await client.perform(urlRequest, decoding: AuthResponse.self)
    }

    func login(request: LoginRequest) async throws -> AuthResponse {
        let urlRequest = try URLRequest.apiRequest(endpoint: .login, method: "POST", body: request)
        return try await client.perform(urlRequest, decoding: AuthResponse.self)
    }
}
