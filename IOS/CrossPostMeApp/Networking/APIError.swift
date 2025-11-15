import Foundation

enum APIError: LocalizedError, Identifiable {
    case invalidURL
    case decodingFailed
    case encodingFailed
    case unauthorized
    case serverError(Int)
    case transport(Error)
    case unknown

    var id: String { localizedDescription }

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "The API endpoint is invalid."
        case .decodingFailed: return "We could not read the server response."
        case .encodingFailed: return "We could not send the request payload."
        case .unauthorized: return "Your session expired. Please sign in again."
        case .serverError(let code): return "Server error (code \(code))."
        case .transport(let error): return error.localizedDescription
        case .unknown: return "Something unexpected happened."
        }
    }
}
