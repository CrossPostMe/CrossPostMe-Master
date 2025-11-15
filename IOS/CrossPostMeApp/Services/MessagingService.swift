import Foundation

protocol MessagingServicing {
    func sendMessage(_ payload: MessagePayload, authToken: String) async throws
    func fetchChatHistory(authToken: String) async throws -> [ChatMessage]
}

final class MessagingService: MessagingServicing {
    private let client: APIRequestPerforming

    init(client: APIRequestPerforming = APIClient()) {
        self.client = client
    }

    func sendMessage(_ payload: MessagePayload, authToken: String) async throws {
        let request = try URLRequest.apiRequest(endpoint: .sendMessage(payload.channel),
                                                method: "POST",
                                                body: payload,
                                                authToken: authToken)
        try await client.perform(request)
    }

    func fetchChatHistory(authToken: String) async throws -> [ChatMessage] {
        let request = try URLRequest.apiRequest(endpoint: .chatHistory,
                                                method: "GET",
                                                authToken: authToken)
        return try await client.perform(request, decoding: [ChatMessage].self)
    }
}
