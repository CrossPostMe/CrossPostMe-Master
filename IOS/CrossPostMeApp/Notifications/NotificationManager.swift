import Foundation
import UserNotifications
import UIKit
import BackgroundTasks

protocol NotificationCoordinating: AnyObject {
    func configure()
    func updateAuthToken(_ token: String?)
    func requestAuthorizationIfNeeded()
    func recordLatestStatus(_ id: UUID?)
    func recordLatestMessage(_ id: UUID?)
}

@MainActor
final class NotificationManager: NSObject, ObservableObject, NotificationCoordinating {
    static let shared = NotificationManager()

    private let center = UNUserNotificationCenter.current()
    private let deviceTokenService: DeviceTokenServicing
    private let statusService: StatusServicing
    private let messagingService: MessagingServicing
    private var pendingDeviceToken: String?
    private var authToken: String?
    private var hasRequestedAuthorization = false

    private let lastStatusKey = "crosspostme.notifications.latestStatus"
    private let lastMessageKey = "crosspostme.notifications.latestMessage"

    private override init() {
        self.deviceTokenService = DeviceTokenService()
        self.statusService = StatusService()
        self.messagingService = MessagingService()
        super.init()
    }

    // MARK: - Configuration

    func configure() {
        center.delegate = self
    }

    func requestAuthorizationIfNeeded() {
        guard !hasRequestedAuthorization else { return }
        hasRequestedAuthorization = true
        Task {
            do {
                let granted = try await center.requestAuthorization(options: [.alert, .badge, .sound])
                if granted {
                    DispatchQueue.main.async {
                        UIApplication.shared.registerForRemoteNotifications()
                    }
                }
            } catch {
                hasRequestedAuthorization = false
            }
        }
    }

    func updateAuthToken(_ token: String?) {
        authToken = token
        Task { await sendPendingTokenIfNeeded() }
    }

    func recordLatestStatus(_ id: UUID?) {
        guard let id else { return }
        UserDefaults.standard.set(id.uuidString, forKey: lastStatusKey)
    }

    func recordLatestMessage(_ id: UUID?) {
        guard let id else { return }
        UserDefaults.standard.set(id.uuidString, forKey: lastMessageKey)
    }

    // MARK: - APNs callbacks

    func handleDeviceToken(_ deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        pendingDeviceToken = token
        Task { await sendPendingTokenIfNeeded() }
    }

    func handleRegistrationFailure(_ error: Error) {
        print("[Notifications] Failed to register for remote notifications: \(error.localizedDescription)")
    }

    private func sendPendingTokenIfNeeded() async {
        guard let token = pendingDeviceToken else { return }
        guard let authToken = authToken else { return }
        do {
            try await deviceTokenService.registerDeviceToken(token, authToken: authToken)
        } catch {
            print("[Notifications] Failed to register device token: \(error)")
            return
        }
    }

    // MARK: - Background refresh

    func performBackgroundRefresh(task: BGTask) {
        guard let refreshTask = task as? BGAppRefreshTask else {
            task.setTaskCompleted(success: false)
            return
        }

        refreshTask.expirationHandler = {
            refreshTask.setTaskCompleted(success: false)
        }

        Task {
            let success = await self.fetchLatestDataAndNotify()
            refreshTask.setTaskCompleted(success: success)
        }
    }

    func fetchLatestDataAndNotify() async -> Bool {
        guard let token = authToken else { return true }
        do {
            async let statuses = statusService.fetchStatuses(authToken: token)
            async let messages = messagingService.fetchChatHistory(authToken: token)
            let latestStatuses = try await statuses
            let latestMessages = try await messages
            await MainActor.run {
                if let newestStatus = latestStatuses.first?.id,
                   newestStatus.uuidString != UserDefaults.standard.string(forKey: lastStatusKey) {
                    UserDefaults.standard.set(newestStatus.uuidString, forKey: lastStatusKey)
                    scheduleLocalNotification(title: "New client status", subtitle: latestStatuses.first?.clientName ?? "", body: latestStatuses.first?.statusText ?? "New update available")
                }
                if let newestMessage = latestMessages.first?.id,
                   newestMessage.uuidString != UserDefaults.standard.string(forKey: lastMessageKey) {
                    UserDefaults.standard.set(newestMessage.uuidString, forKey: lastMessageKey)
                    scheduleLocalNotification(title: "New chat reply", subtitle: latestMessages.first?.sender ?? "", body: latestMessages.first?.body ?? "Open the app to read")
                }
            }
            return true
        } catch {
            print("[Notifications] Background fetch failed: \(error)")
            return false
        }
    }

    private func scheduleLocalNotification(title: String, subtitle: String, body: String) {
        let content = UNMutableNotificationContent()
        content.title = title
        if !subtitle.isEmpty { content.subtitle = subtitle }
        content.body = body
        content.sound = .default

        let request = UNNotificationRequest(identifier: UUID().uuidString,
                                            content: content,
                                            trigger: nil)
        center.add(request)
    }
}

extension NotificationManager: UNUserNotificationCenterDelegate {
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.sound, .banner, .badge])
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        completionHandler()
    }
}
