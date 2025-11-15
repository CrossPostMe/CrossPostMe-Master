import Foundation

struct ChatMessage: Codable, Identifiable, Equatable {
    let id: UUID
    let sender: String
    let body: String
    let createdAt: Date
}
