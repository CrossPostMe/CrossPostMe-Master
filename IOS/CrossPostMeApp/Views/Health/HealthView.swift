import SwiftUI

struct HealthView: View {
    @EnvironmentObject private var shell: AppShellViewModel
    @StateObject private var viewModel = HealthViewModel()

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                statusCard(title: "Health", status: viewModel.healthStatus)
                statusCard(title: "Readiness", status: viewModel.readinessStatus)
                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                }
                Spacer()
            }
            .padding()
            .navigationTitle("System Health")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: { Task { await viewModel.refresh() } }) {
                        if viewModel.isLoading {
                            ProgressView()
                        } else {
                            Label("Refresh", systemImage: "arrow.clockwise")
                        }
                    }
                }
            }
            .onAppear(perform: syncTokenAndRefresh)
            .onChange(of: shell.authToken) { _ in syncTokenAndRefresh() }
        }
    }

    private func statusCard(title: String, status: HealthStatus?) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
            if let status {
                HStack {
                    Label(status.status.capitalized, systemImage: statusIcon(for: status.status))
                        .foregroundStyle(statusColor(for: status.status))
                    Spacer()
                    Text(status.checkedAt.formatted(date: .abbreviated, time: .shortened))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Text(status.endpoint)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            } else {
                Text("No data yet")
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }

    private func statusIcon(for status: String) -> String {
        switch status.lowercased() {
        case "ok", "ready": return "checkmark.circle"
        case "degraded": return "exclamationmark.triangle"
        default: return "xmark.circle"
        }
    }

    private func statusColor(for status: String) -> Color {
        switch status.lowercased() {
        case "ok", "ready": return .green
        case "degraded": return .orange
        default: return .red
        }
    }

    private func syncTokenAndRefresh() {
        viewModel.authToken = shell.authToken
        Task { await viewModel.refresh() }
    }
}

#Preview {
    HealthView()
        .environmentObject(AppShellViewModel())
}
