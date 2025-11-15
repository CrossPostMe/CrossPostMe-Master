import Foundation

enum APIEndpoint {
    case register
    case login
    case statusFeed
    case createStatus
    case sendMessage(ChannelType)
    case chatHistory
    case health
    case readiness
    case registerDeviceToken
    case healthHistory
    case healthIncidents

    var path: String {
        switch self {
        case .register: return "/api/auth/register"
        case .login: return "/api/auth/login"
        case .statusFeed, .createStatus: return "/api/status"
        case .sendMessage(let channel):
            switch channel {
            case .chat: return "/api/chat/send"
            case .email: return "/api/email/send"
            case .whatsapp: return "/api/whatsapp/send"
            }
        case .chatHistory: return "/api/chat/history"
        case .health: return "/api/health"
        case .readiness: return "/api/ready"
        case .registerDeviceToken: return "/api/device-tokens"
        case .healthHistory: return "/api/health/history"
        case .healthIncidents: return "/api/health/incidents"
        }
    }
}
