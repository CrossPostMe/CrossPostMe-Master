import Foundation
import SwiftUI

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var isRegisterMode: Bool = false
    @Published var isProcessing: Bool = false
    @Published var errorMessage: String?

    func toggleMode() {
        withAnimation {
            isRegisterMode.toggle()
            errorMessage = nil
        }
    }

    func submit(using shell: AppShellViewModel) async {
        guard !username.trimmingCharacters(in: .whitespaces).isEmpty,
              !password.isEmpty else {
            errorMessage = "Username and password are required."
            return
        }

        if isRegisterMode && email.trimmingCharacters(in: .whitespaces).isEmpty {
            errorMessage = "Email is required to register."
            return
        }

        isProcessing = true
        errorMessage = nil
        defer { isProcessing = false }

        if isRegisterMode {
            await shell.register(username: username, email: email, password: password)
        } else {
            await shell.login(username: username, password: password)
        }

        errorMessage = shell.activeError
    }
}
