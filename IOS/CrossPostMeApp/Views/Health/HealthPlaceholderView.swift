import SwiftUI

struct HealthPlaceholderView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "heart.text.square")
                .font(.system(size: 64))
                .foregroundStyle(.pink)
            Text("Health dashboard")
                .font(.title2)
            Text("Monitor /api/health and /api/ready checks right from your phone.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

#Preview {
    HealthPlaceholderView()
}
