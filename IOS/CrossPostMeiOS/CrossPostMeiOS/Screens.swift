import SwiftUI

struct DashboardView: View {
    @ObservedObject var viewModel: AdsViewModel
    var onNavigate: (AppRoute) -> Void
    
    private let gridColumns = [
        GridItem(.adaptive(minimum: 140), spacing: 12, alignment: .top)
    ]
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("CrossPostMe Dashboard")
                    .font(.largeTitle.weight(.bold))
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                LazyVGrid(columns: gridColumns, spacing: 12) {
                    StatTile(title: "Total Ads", value: viewModel.dashboardStats.totalAds.description)
                    StatTile(title: "Active", value: viewModel.dashboardStats.activeAds.description)
                    StatTile(title: "Platforms", value: viewModel.dashboardStats.platformsConnected.description)
                    StatTile(title: "Posts", value: viewModel.dashboardStats.totalPosts.description)
                    StatTile(title: "Views", value: viewModel.dashboardStats.totalViews.commaSeparated)
                    StatTile(title: "Leads", value: viewModel.dashboardStats.totalLeads.commaSeparated)
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("Quick Actions")
                        .font(.title2.weight(.semibold))
                    
                    ButtonRow(title: "Create New Ad", systemImage: "plus.circle.fill") {
                        onNavigate(.createAd)
                    }
                    ButtonRow(title: "Manage Platforms", systemImage: "switch.2") {
                        onNavigate(.platformManagement)
                    }
                    ButtonRow(title: "Messaging & Leads", systemImage: "bubble.left.and.bubble.right.fill") {
                        onNavigate(.messaging)
                    }
                    ButtonRow(title: "Login", systemImage: "person.crop.circle") {
                        onNavigate(.login)
                    }
                    ButtonRow(title: "Register", systemImage: "person.crop.circle.badge.plus") {
                        onNavigate(.register)
                    }
                }
                
                VStack(alignment: .leading, spacing: 12) {
                    Text("Your Ads")
                        .font(.title2.weight(.semibold))
                    if viewModel.ads.isEmpty {
                        ContentPlaceholder(text: "No ads yet. Tap \"Create New Ad\" to get started.")
                    } else {
                        VStack(spacing: 12) {
                            ForEach(viewModel.ads) { ad in
                                AdCard(ad: ad)
                            }
                        }
                    }
                }
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
            .background(Color(.systemGroupedBackground))
    }
}

struct LoginView: View {
    var onDismiss: () -> Void
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage: String?
    @State private var isLoading = false
    
    var body: some View {
        Form {
            Section(header: Text("Credentials")) {
                TextField("Email", text: $email)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                SecureField("Password", text: $password)
            }
            
            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }
            
            Button(action: handleLogin) {
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                } else {
                    Text("Login")
                        .frame(maxWidth: .infinity)
                }
            }
            .disabled(isLoading)
        }
        .navigationTitle("Login")
    }
    
    private func handleLogin() {
        guard !email.isEmpty, !password.isEmpty else {
            errorMessage = "Email and password are required"
            return
        }
        errorMessage = nil
        isLoading = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            isLoading = false
            onDismiss()
        }
    }
}

struct RegisterView: View {
    var onDismiss: () -> Void
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage: String?
    @State private var isLoading = false
    
    var body: some View {
        Form {
            Section(header: Text("Account")) {
                TextField("Username", text: $username)
                    .textInputAutocapitalization(.never)
                TextField("Email", text: $email)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                SecureField("Password", text: $password)
            }
            
            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }
            
            Button(action: handleRegister) {
                if isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity)
                } else {
                    Text("Create Account")
                        .frame(maxWidth: .infinity)
                }
            }
            .disabled(isLoading)
        }
        .navigationTitle("Register")
    }
    
    private func handleRegister() {
        guard !username.isEmpty, !email.isEmpty, !password.isEmpty else {
            errorMessage = "All fields are required"
            return
        }
        errorMessage = nil
        isLoading = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            isLoading = false
            onDismiss()
        }
    }
}

struct CreateAdView: View {
    @ObservedObject var viewModel: AdsViewModel
    var onDismiss: () -> Void
    
    @State private var title = ""
    @State private var description = ""
    @State private var price = ""
    @State private var category = ""
    @State private var location = ""
    @State private var autoRenew = false
    @State private var errorMessage: String?
    
    var body: some View {
        Form {
            Section(header: Text("Details")) {
                TextField("Title", text: $title)
                TextField("Description", text: $description, axis: .vertical)
                    .lineLimit(3, reservesSpace: true)
                TextField("Price", text: $price)
                    .keyboardType(.decimalPad)
                TextField("Category", text: $category)
                TextField("Location", text: $location)
                Toggle("Auto Renew", isOn: $autoRenew)
            }
            
            if let errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }
            
            Button("Save Ad", action: handleSave)
                .frame(maxWidth: .infinity)
        }
        .navigationTitle("Create Ad")
    }
    
    private func handleSave() {
        guard !title.isEmpty, !description.isEmpty, !price.isEmpty, !category.isEmpty, !location.isEmpty else {
            errorMessage = "All fields are required"
            return
        }
        guard let amount = Double(price.replacingOccurrences(of: ",", with: ".")) else {
            errorMessage = "Price must be a number"
            return
        }
        viewModel.createAd(title: title, description: description, price: amount, category: category, location: location, autoRenew: autoRenew)
        onDismiss()
    }
}

struct PlatformManagementView: View {
    @ObservedObject var viewModel: AdsViewModel
    var onDismiss: () -> Void
    
    var body: some View {
        List(viewModel.platforms) { platform in
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(platform.name)
                        .font(.headline)
                    Spacer()
                    Text(platform.status.label)
                        .font(.caption.bold())
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(statusColor(platform.status).opacity(0.15))
                        .foregroundColor(statusColor(platform.status))
                        .clipShape(Capsule())
                }
                Text(platform.username)
                    .foregroundStyle(.secondary)
                if let lastSync = platform.lastSync {
                    Text("Last sync " + lastSync.relativeDescription)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Menu("Update Status") {
                    ForEach(PlatformAccount.Status.allCases, id: \.self) { status in
                        Button(status.label) {
                            viewModel.updatePlatformStatus(platform, to: status)
                        }
                    }
                }
                .font(.subheadline)
                .padding(.top, 8)
            }
            .padding(.vertical, 8)
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Platforms")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Done", action: onDismiss)
            }
        }
    }
    
    private func statusColor(_ status: PlatformAccount.Status) -> Color {
        switch status {
        case .connected: return .green
        case .needsAttention: return .orange
        case .notConnected: return .gray
        }
    }
}

struct MessagingView: View {
    @ObservedObject var viewModel: AdsViewModel
    var onDismiss: () -> Void
    
    var body: some View {
        List(viewModel.messages) { message in
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(message.sender)
                        .font(.headline)
                    Spacer()
                    Text(message.platform)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Text(message.preview)
                    .foregroundStyle(.secondary)
                Text(message.receivedAt.relativeDescription)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .padding(.vertical, 6)
        }
        .listStyle(.insetGrouped)
        .navigationTitle("Messaging")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Done", action: onDismiss)
            }
        }
    }
}

// MARK: - Supporting Views

private struct StatTile: View {
    var title: String
    var value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.title3.weight(.semibold))
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(Color.primary.opacity(0.08), lineWidth: 1)
        )
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }
}

private struct ButtonRow: View {
    var title: String
    var systemImage: String
    var action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: systemImage)
                    .imageScale(.large)
                    .foregroundStyle(.accent)
                Text(title)
                    .font(.headline)
                Spacer()
                Image(systemName: "chevron.right")
                    .foregroundStyle(.tertiary)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(Color(.secondarySystemBackground))
            )
        }
        .buttonStyle(.plain)
    }
}

private struct AdCard: View {
    var ad: Ad
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(ad.title)
                    .font(.headline)
                Spacer()
                Text(ad.status.label)
                    .font(.caption.bold())
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.accentColor.opacity(0.15))
                    .foregroundColor(.accentColor)
                    .clipShape(Capsule())
            }
            Text(ad.description)
                .foregroundStyle(.secondary)
            HStack {
                Label(ad.price.formattedCurrency, systemImage: "dollarsign.circle")
                Spacer()
                Label(ad.location, systemImage: "mappin.and.ellipse")
            }
            .font(.subheadline)
            
            if !ad.platforms.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(ad.platforms, id: \.self) { platform in
                            Text(platform)
                                .font(.caption)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.accentColor.opacity(0.1))
                                .clipShape(Capsule())
                        }
                    }
                }
            }
            
            HStack {
                Label("Posts: \(ad.totalPosts)", systemImage: "square.and.arrow.up")
                Spacer()
                Label("Views: \(ad.totalViews)", systemImage: "eye")
                Spacer()
                Label("Leads: \(ad.totalLeads)", systemImage: "person.crop.circle.badge.questionmark")
            }
            .font(.caption)
            .foregroundStyle(.secondary)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.04), radius: 6, y: 3)
        )
    }
}

private struct ContentPlaceholder: View {
    var text: String
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "tray")
                .font(.largeTitle)
                .foregroundStyle(.tertiary)
            Text(text)
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color(.secondarySystemBackground))
        )
    }
}

private extension Int {
    var commaSeparated: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        return formatter.string(for: self) ?? String(self)
    }
}

private extension Double {
    var formattedCurrency: String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        return formatter.string(for: self) ?? "$0"
    }
}

private extension Date {
    var relativeDescription: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .full
        return formatter.localizedString(for: self, relativeTo: Date())
    }
}

