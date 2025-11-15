import Foundation
import SwiftUI
import Combine

@MainActor
final class MessagingViewModel: ObservableObject {
    @Published var selectedChannel: ChannelType = .chat
    @Published var recipient: String = ""
    @Published var subject: String = ""
    @Published var body: String = ""
    @Published private(set) var chatHistory: [ChatMessage] = []
    @Published private(set) var isSending = false
    @Published private(set) var isRefreshingHistory = false
    @Published var errorMessage: String?
    @Published var successBanner: String?
    @Published var aiSuggestion: String?
    @Published private(set) var isGeneratingSuggestion = false
    @Published private(set) var sentimentByMessage: [UUID: Sentiment] = [:]
    @Published private(set) var isAnalyzingSentiment = false

    var authToken: String?

    private let service: MessagingServicing
    private let aiService: AIComposeServicing
    private var cancellables: Set<AnyCancellable> = []

    init(service: MessagingServicing = MessagingService(),
         aiService: AIComposeServicing = AIComposeService()) {
        self.service = service
        self.aiService = aiService
        SupabaseRealtimeCoordinator.shared.chatPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] message in
                self?.applyRealtimeMessage(message)
            }
            .store(in: &cancellables)
    }

    func loadInitialData() {
        Task { await refreshHistory() }
    }

    func refreshHistory() async {
        guard let token = authToken else {
            chatHistory = []
            return
        }
        isRefreshingHistory = true
        defer { isRefreshingHistory = false }
        do {
            chatHistory = try await service.fetchChatHistory(authToken: token)
            NotificationManager.shared.recordLatestMessage(chatHistory.first?.id)
            await analyzeSentiment()
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    func sendMessage() async {
        guard let token = authToken else {
            errorMessage = "Please sign in first."
            return
        }

        let trimmedBody = body.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedBody.isEmpty else {
            errorMessage = "Message body cannot be empty."
            return
        }

        isSending = true
        errorMessage = nil
        defer { isSending = false }

        let payload = MessagePayload(channel: selectedChannel,
                                     recipient: recipient,
                                     subject: subject.isEmpty ? nil : subject,
                                     body: trimmedBody)
        do {
            try await service.sendMessage(payload, authToken: token)
            successBanner = "Sent via \(selectedChannel.title)"
            body = ""
            subject = ""
            if selectedChannel == .chat {
                await refreshHistory()
            }
        } catch {
            errorMessage = (error as? APIError)?.localizedDescription ?? error.localizedDescription
        }
    }

    func requestAISuggestion() async {
        guard !isGeneratingSuggestion else { return }
        isGeneratingSuggestion = true
        errorMessage = nil
        defer { isGeneratingSuggestion = false }

        var context = chatHistory.prefix(5).map { "\($0.sender): \($0.body)" }.joined(separator: "\n")
        if context.isEmpty {
            context = body.isEmpty ? "No prior history" : body
        }

        do {
            let suggestion = try await aiService.generateReply(context: context, channel: selectedChannel)
            await MainActor.run {
                aiSuggestion = suggestion
                body = suggestion
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func dismissAISuggestion() {
        aiSuggestion = nil
    }

    func acceptAISuggestion() {
        guard let suggestion = aiSuggestion else { return }
        body = suggestion
    }

    private func analyzeSentiment() async {
        guard !chatHistory.isEmpty else {
            sentimentByMessage = [:]
            return
        }
        isAnalyzingSentiment = true
        defer { isAnalyzingSentiment = false }
        var updated: [UUID: Sentiment] = [:]
        for message in chatHistory.prefix(20) {
            do {
                let sentiment = try await aiService.analyzeSentiment(for: message.body)
                updated[message.id] = sentiment
            } catch {
                continue
            }
        }
        await MainActor.run {
            sentimentByMessage = updated
        }
    }

    private func applyRealtimeMessage(_ message: ChatMessage) {
        if chatHistory.contains(where: { $0.id == message.id }) {
            return
        }
        chatHistory.insert(message, at: 0)
        NotificationManager.shared.recordLatestMessage(message.id)
        Task { await analyzeSentiment() }
    }
}
