import SwiftUI

struct AppRootView: View {
    @EnvironmentObject private var shell: AppShellViewModel

    var body: some View {
        switch shell.authState {
        case .loading:
            ProgressView("Loading…")
                .progressViewStyle(.circular)
        case .signedOut:
            AuthView()
        case .authenticated:
            MainTabView()
        }
    }
}

private struct MainTabView: View {
    @EnvironmentObject private var shell: AppShellViewModel

    var body: some View {
        TabView {
            DashboardView()
                .tabItem { Label("Status", systemImage: "list.bullet") }

            MessagingPlaceholderView()
                .tabItem { Label("Message", systemImage: "paperplane") }

            HealthPlaceholderView()
                .tabItem { Label("Health", systemImage: "heart.circle") }
        }
        .overlay(alignment: .topTrailing) {
            if let user = shell.currentUser {
                Text("Signed in as \(user.username)")
                    .font(.caption)
                    .padding(8)
                    .background(.ultraThinMaterial, in: Capsule())
                    .padding([.top, .trailing], 12)
            }
        }
    }
}

#Preview {
    AppRootView()
        .environmentObject(AppShellViewModel())
}
