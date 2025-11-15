import Foundation

enum Sentiment: String, Codable {
    case positive
    case neutral
    case negative
}

protocol AIComposeServicing {
    func generateReply(context: String, channel: ChannelType) async throws -> String
    func analyzeSentiment(for text: String) async throws -> Sentiment
}

enum AIComposeError: LocalizedError {
    case configurationMissing
    case invalidResponse
    case serviceUnavailable(String)

    var errorDescription: String? {
        switch self {
        case .configurationMissing:
            return "AI configuration is missing."
        case .invalidResponse:
            return "AI service returned an unexpected response."
        case .serviceUnavailable(let message):
            return message
        }
    }
}

final class AIComposeService: AIComposeServicing {
    private let session: URLSession
    private let logger = NetworkLogger()

    init(session: URLSession = .shared) {
        self.session = session
    }

    func generateReply(context: String, channel: ChannelType) async throws -> String {
        let prompt = "You are CrossPostMe, a helpful assistant. Craft a concise, friendly \(channel.title.lowercased()) response based on the conversation below. Respond with plain text only. Conversation: \n\(context)"
        let requestBody = ChatCompletionRequest(messages: [
            .init(role: "system", content: "You are an efficient assistant for customer communication."),
            .init(role: "user", content: prompt)
        ])
        let response = try await performChatCompletion(request: requestBody)
        guard let suggestion = response else { throw AIComposeError.invalidResponse }
        return suggestion
    }

    func analyzeSentiment(for text: String) async throws -> Sentiment {
        let instruction = "Classify the sentiment of the following message as positive, neutral, or negative. Reply with one word only. Message: \n\(text)"
        let requestBody = ChatCompletionRequest(messages: [
            .init(role: "system", content: "You analyze sentiment for operator escalations."),
            .init(role: "user", content: instruction)
        ])
        guard let output = try await performChatCompletion(request: requestBody) else {
            throw AIComposeError.invalidResponse
        }
        let normalized = output.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        if normalized.contains("positive") { return .positive }
        if normalized.contains("negative") { return .negative }
        return .neutral
    }

    // MARK: - Private helpers

    private func performChatCompletion(request: ChatCompletionRequest) async throws -> String? {
        guard
            let baseURL = AppConfig.current.azureOpenAIBaseURL,
            let deployment = AppConfig.current.azureOpenAIDeployment,
            let apiVersion = AppConfig.current.azureOpenAIAPIVersion,
            let apiKey = AppConfig.current.azureOpenAIAPIKey
        else {
            throw AIComposeError.configurationMissing
        }

        var url = baseURL
        url.appendPathComponent("openai/deployments/\(deployment)/chat/completions")
        guard var components = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            throw AIComposeError.configurationMissing
        }
        components.queryItems = [URLQueryItem(name: "api-version", value: apiVersion)]
        guard let finalURL = components.url else {
            throw AIComposeError.configurationMissing
        }

        var urlRequest = URLRequest(url: finalURL)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue(apiKey, forHTTPHeaderField: "api-key")
        urlRequest.httpBody = try JSONEncoder().encode(request)

        do {
            let (data, response) = try await session.data(for: urlRequest)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw AIComposeError.invalidResponse
            }
            guard 200..<300 ~= httpResponse.statusCode else {
                let body = String(data: data, encoding: .utf8) ?? ""
                throw AIComposeError.serviceUnavailable(body)
            }
            let completion = try JSONDecoder().decode(ChatCompletionResponse.self, from: data)
            return completion.choices.first?.message.firstText
        } catch {
            logger.log(.error, "AI compose failed: \(error)")
            throw error
        }
    }
}

private struct ChatCompletionRequest: Codable {
    struct ChatMessage: Codable {
        let role: String
        let content: String
    }

    let messages: [ChatMessage]
    let temperature: Double = 0.3
    let top_p: Double = 0.95
}

private struct ChatCompletionResponse: Codable {
    struct Choice: Codable {
        struct Message: Codable {
            struct ContentBlock: Codable {
                let type: String?
                let text: String?
            }
            let content: [ContentBlock]?
        }
        let message: Message
    }
    let choices: [Choice]
}

private extension ChatCompletionResponse.Choice.Message {
    var firstText: String? {
        content?.first?.text
    }
}
*** End Patch