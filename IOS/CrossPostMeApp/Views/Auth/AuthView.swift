import SwiftUI

struct AuthView: View {
    @EnvironmentObject private var shell: AppShellViewModel
    @StateObject private var viewModel = AuthViewModel()

    var body: some View {
        NavigationStack {
            Form {
                Section(viewModel.isRegisterMode ? "Create account" : "Welcome back") {
                    TextField("Username", text: $viewModel.username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    if viewModel.isRegisterMode {
                        TextField("Email", text: $viewModel.email)
                            .textInputAutocapitalization(.never)
                            .keyboardType(.emailAddress)
                    }

                    SecureField("Password", text: $viewModel.password)
                }

                Section {
                    Button(action: submit) {
                        if viewModel.isProcessing {
                            ProgressView()
                        } else {
                            Text(viewModel.isRegisterMode ? "Create Account" : "Sign In")
                                .frame(maxWidth: .infinity)
                        }
                    }
                }

                Section {
                    Button(viewModel.isRegisterMode ? "Have an account? Sign in" : "Need an account? Register") {
                        viewModel.toggleMode()
                    }
                    .buttonStyle(.borderless)
                }

                if let error = viewModel.errorMessage {
                    Section {
                        Text(error)
                            .font(.footnote)
                            .foregroundStyle(.red)
                    }
                }
            }
            .navigationTitle("CrossPostMe")
        }
    }

    private func submit() {
        Task {
            await viewModel.submit(using: shell)
        }
    }
}

#Preview {
    AuthView()
        .environmentObject(AppShellViewModel())
}
