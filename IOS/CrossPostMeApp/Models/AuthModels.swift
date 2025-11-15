import Foundation

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct RegisterRequest: Codable {
    let username: String
    let email: String
    let password: String
}

struct AuthResponse: Codable {
    let user: User
    let accessToken: String
    let refreshToken: String?
}
