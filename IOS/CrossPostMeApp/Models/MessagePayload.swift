import Foundation

enum ChannelType: String, Codable, CaseIterable, Identifiable {
    case chat
    case email
    case whatsapp

    var id: String { rawValue }
    var title: String {
        switch self {
        case .chat: return "Chat"
        case .email: return "Email"
        case .whatsapp: return "WhatsApp"
        }
    }
}

struct MessagePayload: Codable {
    let channel: ChannelType
    let recipient: String
    let subject: String?
    let body: String
}
