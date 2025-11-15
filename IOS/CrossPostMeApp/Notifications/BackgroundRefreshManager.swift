import Foundation
import BackgroundTasks

final class BackgroundRefreshManager {
    static let shared = BackgroundRefreshManager()
    private let taskIdentifier = "com.crosspostme.app.refresh"

    private init() {}

    func registerTasks() {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: taskIdentifier, using: nil) { task in
            NotificationManager.shared.performBackgroundRefresh(task: task)
        }
    }

    func scheduleAppRefresh(after interval: TimeInterval = 60 * 30) {
        let request = BGAppRefreshTaskRequest(identifier: taskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: interval)
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("[BackgroundRefresh] Failed to schedule task: \(error)")
        }
    }
}
