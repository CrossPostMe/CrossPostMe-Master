import SwiftUI

struct MessagingPlaceholderView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "paperplane.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("Messaging coming soon")
                .font(.title2)
            Text("We are building a unified composer for Chat, Email, and WhatsApp. Stay tuned!")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

#Preview {
    MessagingPlaceholderView()
}
