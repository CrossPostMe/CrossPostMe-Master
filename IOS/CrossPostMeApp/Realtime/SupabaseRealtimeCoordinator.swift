import Foundation
import Combine
#if canImport(Supabase)
import Supabase
#endif

final class SupabaseRealtimeCoordinator {
    static let shared = SupabaseRealtimeCoordinator()

    #if canImport(Supabase)
    private var client: SupabaseClient?
    private var statusChannel: RealtimeChannel?
    private var chatChannel: RealtimeChannel?
    #endif

    private let statusSubject = PassthroughSubject<StatusEntry, Never>()
    private let chatSubject = PassthroughSubject<ChatMessage, Never>()

    var statusPublisher: AnyPublisher<StatusEntry, Never> {
        statusSubject.eraseToAnyPublisher()
    }

    var chatPublisher: AnyPublisher<ChatMessage, Never> {
        chatSubject.eraseToAnyPublisher()
    }

    private init() {}

    func connectIfPossible(authToken: String?) {
        #if canImport(Supabase)
        if client != nil {
            setRealtimeAuth(token: authToken)
            return
        }

        guard let supabaseURL = AppConfig.current.supabaseURL,
              let supabaseAnonKey = AppConfig.current.supabaseAnonKey else {
            print("[Realtime] Missing Supabase configuration. Skipping realtime updates.")
            return
        }

        client = SupabaseClient(supabaseURL: supabaseURL, supabaseKey: supabaseAnonKey)
        setRealtimeAuth(token: authToken)
        Task { await subscribeToChannels() }
        #endif
    }

    func disconnect() {
        #if canImport(Supabase)
        Task {
            await statusChannel?.unsubscribe()
            await chatChannel?.unsubscribe()
        }
        client?.realtime.disconnect()
        client = nil
        statusChannel = nil
        chatChannel = nil
        #endif
    }

    // MARK: - Private helpers

    #if canImport(Supabase)
    private func setRealtimeAuth(token: String?) {
        guard let client else { return }
        if let token {
            client.realtime.setAuth(token)
        } else {
            client.realtime.setAuth(nil)
        }
    }

    private func subscribeToChannels() async {
        await subscribeToStatuses()
        await subscribeToChatMessages()
    }

    private func subscribeToStatuses() async {
        guard let client else { return }
        let channel = client.channel("public:status_entries")
        channel.on(
            .postgresChanges,
            filter: PostgresChangeFilter(event: .insert, schema: "public", table: "status_entries")
        ) { [weak self] payload in
            if let status = try? payload.decodeRecord(as: StatusEntry.self) {
                self?.statusSubject.send(status)
            }
        }
        channel.on(
            .postgresChanges,
            filter: PostgresChangeFilter(event: .update, schema: "public", table: "status_entries")
        ) { [weak self] payload in
            if let status = try? payload.decodeRecord(as: StatusEntry.self) {
                self?.statusSubject.send(status)
            }
        }
        _ = await channel.subscribe()
        statusChannel = channel
    }

    private func subscribeToChatMessages() async {
        guard let client else { return }
        let channel = client.channel("public:chat_messages")
        channel.on(
            .postgresChanges,
            filter: PostgresChangeFilter(event: .insert, schema: "public", table: "chat_messages")
        ) { [weak self] payload in
            if let message = try? payload.decodeRecord(as: ChatMessage.self) {
                self?.chatSubject.send(message)
            }
        }
        _ = await channel.subscribe()
        chatChannel = channel
    }
    #endif
}
*** End Patch