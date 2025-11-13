import SwiftUI

@main
struct CrossPostMeiOSApp: App {
    @StateObject private var viewModel = AdsViewModel()
    
    var body: some Scene {
        WindowGroup {
            RootView(viewModel: viewModel)
        }
    }
}

enum AppRoute: Hashable {
    case login
    case register
    case createAd
    case platformManagement
    case messaging
}

struct RootView: View {
    @ObservedObject var viewModel: AdsViewModel
    @State private var path: [AppRoute] = []
    
    var body: some View {
        NavigationStack(path: $path) {
            DashboardView(viewModel: viewModel) { route in
                path.append(route)
            }
            .navigationDestination(for: AppRoute.self) { route in
                switch route {
                case .login:
                    LoginView {
                        path.removeAll()
                    }
                case .register:
                    RegisterView {
                        path.removeAll()
                    }
                case .createAd:
                    CreateAdView(viewModel: viewModel) {
                        path.removeAll()
                    }
                case .platformManagement:
                    PlatformManagementView(viewModel: viewModel) {
                        path.removeAll()
                    }
                case .messaging:
                    MessagingView(viewModel: viewModel) {
                        path.removeAll()
                    }
                }
            }
            .navigationTitle("CrossPostMe")
        }
    }
}
