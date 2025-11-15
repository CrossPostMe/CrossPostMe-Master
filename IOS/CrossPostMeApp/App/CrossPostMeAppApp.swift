import SwiftUI

@main
struct CrossPostMeAppApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var appShellViewModel = AppShellViewModel()

    var body: some Scene {
        WindowGroup {
            AppRootView()
                .environmentObject(appShellViewModel)
                .task {
                    await appShellViewModel.bootstrap()
                    NotificationManager.shared.requestAuthorizationIfNeeded()
                }
        }
    }
}
