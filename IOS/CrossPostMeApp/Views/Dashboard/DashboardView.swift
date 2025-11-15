import SwiftUI

struct DashboardView: View {
    @EnvironmentObject private var shell: AppShellViewModel
    @StateObject private var statusViewModel = StatusTimelineViewModel()

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                composer
                statusList
            }
            .padding()
            .navigationTitle("Status Feed")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Refresh") {
                        Task { await statusViewModel.reloadIfPossible() }
                    }
                    .disabled(statusViewModel.authToken == nil)
                }
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Sign Out") { shell.logout() }
                }
            }
            .onAppear(perform: syncAuthToken)
            .onChange(of: shell.authToken) { _ in syncAuthToken() }
        }
    }

    private var composer: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Share an update")
                .font(.headline)
            TextEditor(text: $statusViewModel.composerText)
                .frame(minHeight: 80)
                .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.secondary.opacity(0.3)))
            Button(action: submitStatus) {
                if statusViewModel.isLoading {
                    ProgressView()
                } else {
                    Text("Post Update")
                        .bold()
                        .frame(maxWidth: .infinity)
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(statusViewModel.authToken == nil || statusViewModel.composerText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
            if let error = statusViewModel.errorMessage {
                Text(error)
                    .font(.footnote)
                    .foregroundStyle(.red)
            }
        }
    }

    private var statusList: some View {
        Group {
            if statusViewModel.statuses.isEmpty {
                ContentUnavailableView("No updates yet", systemImage: "tray")
            } else {
                List(statusViewModel.statuses) { entry in
                    VStack(alignment: .leading, spacing: 4) {
                        Text(entry.clientName)
                            .font(.headline)
                        Text(entry.statusText)
                        Text(entry.createdAt.formatted(date: .abbreviated, time: .shortened))
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)
                }
                .listStyle(.plain)
            }
        }
    }

    private func syncAuthToken() {
        statusViewModel.authToken = shell.authToken
    }

    private func submitStatus() {
        guard let token = shell.authToken else { return }
        Task { await statusViewModel.submitStatus(token: token) }
    }
}

#Preview {
    DashboardView()
        .environmentObject(AppShellViewModel())
}
