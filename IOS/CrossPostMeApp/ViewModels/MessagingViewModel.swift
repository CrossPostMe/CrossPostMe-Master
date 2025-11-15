import Foundation
import SwiftUI

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

    var authToken: String?

    private let service: MessagingServicing

    init(service: MessagingServicing = MessagingService()) {
        self.service = service
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
}
