import SwiftUI

struct MessagingView: View {
    @EnvironmentObject private var shell: AppShellViewModel
    @StateObject private var viewModel = MessagingViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    channelPicker
                    recipientFields
                    bodyField
                    aiAssistantSection
                    sendButton
                    historySection
                }
                .padding()
            }
            .navigationTitle("Messaging Hub")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Refresh") { Task { await viewModel.refreshHistory() } }
                        .disabled(viewModel.isRefreshingHistory)
                }
                ToolbarItem(placement: .topBarLeading) {
                    Button("Suggest Reply") { Task { await viewModel.requestAISuggestion() } }
                        .disabled(viewModel.isGeneratingSuggestion)
                }
            }
            .onAppear(perform: syncAuthToken)
            .onChange(of: shell.authToken) { _ in syncAuthToken() }
        }
        .alert(viewModel.successBanner ?? "", isPresented: Binding(
            get: { viewModel.successBanner != nil },
            set: { if !$0 { viewModel.successBanner = nil } }
        )) {
            Button("OK", role: .cancel) { viewModel.successBanner = nil }
        }
    }

    private var channelPicker: some View {
        Picker("Channel", selection: $viewModel.selectedChannel) {
            ForEach(ChannelType.allCases) { channel in
                Text(channel.title).tag(channel)
            }
        }
        .pickerStyle(.segmented)
    }

    private var recipientFields: some View {
        VStack(alignment: .leading, spacing: 12) {
            TextField("Recipient", text: $viewModel.recipient)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
            if viewModel.selectedChannel != .chat {
                TextField("Subject (optional)", text: $viewModel.subject)
            }
        }
    }

    private var bodyField: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Message")
                .font(.headline)
            TextEditor(text: $viewModel.body)
                .frame(minHeight: 150)
                .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.secondary.opacity(0.3)))
        }
    }

    private var sendButton: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button(action: { Task { await viewModel.sendMessage() } }) {
                if viewModel.isSending {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                } else {
                    Text("Send via \(viewModel.selectedChannel.title)")
                        .bold()
                        .frame(maxWidth: .infinity)
                }
            }
            .buttonStyle(.borderedProminent)

            if let error = viewModel.errorMessage {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
            }
        }
    }

    private var aiAssistantSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("AI Assist")
                    .font(.headline)
                Spacer()
                if viewModel.isGeneratingSuggestion {
                    ProgressView()
                } else {
                    Button("Suggest draft") {
                        Task { await viewModel.requestAISuggestion() }
                    }
                }
            }
            if let suggestion = viewModel.aiSuggestion {
                VStack(alignment: .leading, spacing: 8) {
                    Text(suggestion)
                        .font(.body)
                    HStack {
                        Button("Use suggestion") {
                            viewModel.acceptAISuggestion()
                        }
                        Button("Dismiss", role: .destructive) {
                            viewModel.dismissAISuggestion()
                        }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                .background(.ultraThickMaterial, in: RoundedRectangle(cornerRadius: 12))
            } else {
                Text("Let Azure AI craft a contextual reply for you.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var historySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Recent chat history")
                    .font(.headline)
                Spacer()
                if viewModel.isRefreshingHistory {
                    ProgressView()
                }
            }

            if viewModel.chatHistory.isEmpty {
                ContentUnavailableView("No chat messages yet", systemImage: "bubble.left.and.bubble.right")
            } else {
                ForEach(viewModel.chatHistory) { message in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(message.sender)
                                .font(.subheadline)
                                .bold()
                            Spacer()
                            Text(message.createdAt.formatted(date: .abbreviated, time: .shortened))
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                        Text(message.body)
                        if let sentiment = viewModel.sentimentByMessage[message.id] {
                            sentimentChip(for: sentiment)
                        }
                    }
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 12))
                }
            }
        }
    }

    private func sentimentChip(for sentiment: Sentiment) -> some View {
        let (text, color, icon): (String, Color, String) = {
            switch sentiment {
            case .positive: return ("Positive", .green, "hand.thumbsup.fill")
            case .neutral: return ("Neutral", .gray, "minus.circle")
            case .negative: return ("Negative", .red, "exclamationmark.triangle.fill")
            }
        }()
        return Label(text, systemImage: icon)
            .font(.caption)
            .padding(.horizontal, 10)
            .padding(.vertical, 4)
            .background(color.opacity(0.15), in: Capsule())
            .foregroundStyle(color)
    }

    private func syncAuthToken() {
        viewModel.authToken = shell.authToken
        viewModel.loadInitialData()
    }
}

#Preview {
    MessagingView()
        .environmentObject(AppShellViewModel())
}
