import Foundation

struct StatusEntry: Codable, Identifiable {
    let id: UUID
    let clientName: String
    let statusText: String
    let createdAt: Date
}
