import Foundation
import SwiftUI

@MainActor
final class AppShellViewModel: ObservableObject {
    enum AuthState: Equatable {
        case loading
        case signedOut
        case authenticated(user: User, token: String)
    }

    @Published private(set) var authState: AuthState = .loading
    @Published var activeError: String?

    private let authService: AuthServicing
    private let tokenStore: TokenStore
    private let userDefaults: UserDefaults

    private let tokenKey = "crosspostme.auth.token"
    private let userKey = "crosspostme.auth.user"

    init(authService: AuthServicing = AuthService(),
         tokenStore: TokenStore = SecureStore(),
         userDefaults: UserDefaults = .standard) {
        self.authService = authService
        self.tokenStore = tokenStore
        self.userDefaults = userDefaults
    }

    var isAuthenticated: Bool {
        if case .authenticated = authState { return true }
        return false
    }

    var currentUser: User? {
        if case .authenticated(let user, _) = authState { return user }
        return nil
    }

    var authToken: String? {
        if case .authenticated(_, let token) = authState { return token }
        return nil
    }

    func bootstrap() async {
        authState = .loading
        defer { if case .loading = authState { authState = .signedOut } }
        do {
            let token = try tokenStore.readToken(for: tokenKey)
            let user = try loadStoredUser()
            guard let token, let user else {
                authState = .signedOut
                return
            }
            authState = .authenticated(user: user, token: token)
        } catch {
            authState = .signedOut
        }
    }

    func login(username: String, password: String) async {
        activeError = nil
        do {
            let response = try await authService.login(request: .init(username: username, password: password))
            try persistSession(response)
            authState = .authenticated(user: response.user, token: response.accessToken)
        } catch {
            activeError = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    func register(username: String, email: String, password: String) async {
        activeError = nil
        do {
            let response = try await authService.register(request: .init(username: username, email: email, password: password))
            try persistSession(response)
            authState = .authenticated(user: response.user, token: response.accessToken)
        } catch {
            activeError = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    func logout() {
        try? tokenStore.deleteToken(for: tokenKey)
        userDefaults.removeObject(forKey: userKey)
        authState = .signedOut
    }

    // MARK: - Private helpers

    private func persistSession(_ response: AuthResponse) throws {
        try tokenStore.save(token: response.accessToken, key: tokenKey)
        let data = try JSONEncoder().encode(response.user)
        userDefaults.set(data, forKey: userKey)
    }

    private func loadStoredUser() throws -> User? {
        guard let data = userDefaults.data(forKey: userKey) else { return nil }
        return try JSONDecoder().decode(User.self, from: data)
    }
}
