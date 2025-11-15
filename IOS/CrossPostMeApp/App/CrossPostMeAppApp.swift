import SwiftUI

@main
struct CrossPostMeAppApp: App {
    @StateObject private var appShellViewModel = AppShellViewModel()

    var body: some Scene {
        WindowGroup {
            AppRootView()
                .environmentObject(appShellViewModel)
                .task {
                    await appShellViewModel.bootstrap()
                }
        }
    }
}
