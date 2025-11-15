import SwiftUI
import Charts

struct HealthView: View {
    @EnvironmentObject private var shell: AppShellViewModel
    @StateObject private var viewModel = HealthViewModel()
    @StateObject private var analyticsViewModel = HealthAnalyticsViewModel()

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    statusCard(title: "Health", status: viewModel.healthStatus)
                    statusCard(title: "Readiness", status: viewModel.readinessStatus)
                    metricsOverview
                    analyticsChartSection
                    incidentsSection
                    if let error = viewModel.errorMessage ?? analyticsViewModel.errorMessage {
                        Text(error)
                            .foregroundStyle(.red)
                            .multilineTextAlignment(.center)
                    }
                }
                .padding()
            }
            .navigationTitle("System Health")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button(action: refreshAll) {
                        if viewModel.isLoading || analyticsViewModel.isLoading {
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

    private var metricsOverview: some View {
        HStack(spacing: 16) {
            metricCard(title: "Uptime (24h)",
                      value: analyticsViewModel.uptimePercentage.isNaN ? "--" : String(format: "%.1f%%", analyticsViewModel.uptimePercentage),
                      subtitle: "Healthy windows vs. total samples")
            metricCard(title: "Avg latency",
                      value: analyticsViewModel.averageLatency.map { String(format: "%.0f ms", $0) } ?? "--",
                      subtitle: "Rolling mean from history")
        }
    }

    private var analyticsChartSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Latency trend")
                    .font(.headline)
                Spacer()
                if analyticsViewModel.isLoading {
                    ProgressView()
                }
            }
            if analyticsViewModel.recentHistory.isEmpty {
                ContentUnavailableView("No history yet", systemImage: "waveform.path.ecg")
            } else {
                Chart(analyticsViewModel.recentHistory) { point in
                    LineMark(
                        x: .value("Time", point.timestamp),
                        y: .value("Latency", point.latencyMs)
                    )
                    .foregroundStyle(by: .value("Status", point.status.capitalized))
                    AreaMark(
                        x: .value("Time", point.timestamp),
                        y: .value("Latency", point.latencyMs)
                    )
                    .interpolationMethod(.catmullRom)
                    .foregroundStyle(Gradient(colors: [.green.opacity(0.2), .green.opacity(0.01)]))
                }
                .frame(height: 220)
                .chartXAxis {
                    AxisMarks(position: .bottom, values: .automatic(desiredCount: 4))
                }
                .chartYAxis {
                    AxisMarks(position: .leading)
                }
            }
        }
    }

    private var incidentsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Incident log")
                    .font(.headline)
                Spacer()
            }
            if analyticsViewModel.incidents.isEmpty {
                ContentUnavailableView("No incidents recorded", systemImage: "checkmark.seal")
            } else {
                ForEach(analyticsViewModel.incidents) { incident in
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(incident.title)
                                .font(.subheadline)
                                .bold()
                            Spacer()
                            severityBadge(incident.severity)
                        }
                        Text(incident.details)
                        HStack {
                            Label(incident.startedAt.formatted(date: .abbreviated, time: .shortened), systemImage: "play.circle")
                                .font(.caption)
                            if let resolved = incident.resolvedAt {
                                Label(resolved.formatted(date: .abbreviated, time: .shortened), systemImage: "stop.circle")
                                    .font(.caption)
                            }
                        }
                        .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
                }
            }
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

    private func metricCard(title: String, value: String, subtitle: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.title2)
                .bold()
            Text(subtitle)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 16))
    }

    private func severityBadge(_ severity: String) -> some View {
        let color: Color
        switch severity.lowercased() {
        case "critical": color = .red
        case "major": color = .orange
        case "minor": color = .yellow
        default: color = .gray
        }
        return Text(severity.capitalized)
            .font(.caption)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.2), in: Capsule())
            .foregroundStyle(color)
    }

    private func syncTokenAndRefresh() {
        viewModel.authToken = shell.authToken
        analyticsViewModel.authToken = shell.authToken
        refreshAll()
    }

    private func refreshAll() {
        Task {
            async let statusTask: Void = viewModel.refresh()
            async let analyticsTask: Void = analyticsViewModel.refresh()
            _ = await (statusTask, analyticsTask)
        }
    }
}

#Preview {
    HealthView()
        .environmentObject(AppShellViewModel())
}
