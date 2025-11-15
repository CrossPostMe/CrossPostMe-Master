import Foundation

struct User: Codable, Identifiable, Equatable {
    let id: UUID
    let username: String
    let email: String
    let isActive: Bool
}
