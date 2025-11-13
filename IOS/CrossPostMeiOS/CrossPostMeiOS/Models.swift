import Foundation

struct Ad: Identifiable, Hashable {
    enum Status: String, CaseIterable, Identifiable {
        case draft
        case scheduled
        case active
        case paused
        case completed
        
        var id: String { rawValue }
        var label: String {
            switch self {
            case .draft: return "Draft"
            case .scheduled: return "Scheduled"
            case .active: return "Active"
            case .paused: return "Paused"
            case .completed: return "Completed"
            }
        }
    }
    
    let id: UUID
    var title: String
    var description: String
    var price: Double
    var category: String
    var location: String
    var status: Status
    var platforms: [String]
    var totalPosts: Int
    var totalViews: Int
    var totalLeads: Int
    var createdAt: Date
    var scheduledTime: Date?
    var autoRenew: Bool
}

struct DashboardStats {
    var totalAds: Int
    var activeAds: Int
    var platformsConnected: Int
    var totalPosts: Int
    var totalViews: Int
    var totalLeads: Int
}

struct PlatformAccount: Identifiable, Hashable {
    enum Status: String, CaseIterable {
        case connected
        case needsAttention
        case notConnected
        
        var label: String {
            switch self {
            case .connected: return "Connected"
            case .needsAttention: return "Needs Attention"
            case .notConnected: return "Not Connected"
            }
        }
    }
    
    let id = UUID()
    var name: String
    var username: String
    var status: Status
    var lastSync: Date?
}

struct LeadMessage: Identifiable, Hashable {
    let id = UUID()
    var sender: String
    var platform: String
    var preview: String
    var receivedAt: Date
}

struct MockData {
    static let shared = MockData()
    
    let ads: [Ad]
    let platforms: [PlatformAccount]
    let messages: [LeadMessage]
    
    private init() {
        let now = Date()
        ads = [
            Ad(
                id: UUID(),
                title: "Vintage Road Bike",
                description: "A well-maintained road bike perfect for weekend rides.",
                price: 420.0,
                category: "Sports",
                location: "Austin, TX",
                status: .active,
                platforms: ["Facebook Marketplace", "Craigslist"],
                totalPosts: 6,
                totalViews: 1120,
                totalLeads: 32,
                createdAt: now.addingTimeInterval(-86400 * 10),
                scheduledTime: nil,
                autoRenew: true
            ),
            Ad(
                id: UUID(),
                title: "Mid-century Desk",
                description: "Solid walnut desk with hidden cable management.",
                price: 950.0,
                category: "Home Office",
                location: "Denver, CO",
                status: .scheduled,
                platforms: ["Etsy"],
                totalPosts: 2,
                totalViews: 540,
                totalLeads: 9,
                createdAt: now.addingTimeInterval(-86400 * 3),
                scheduledTime: now.addingTimeInterval(3600 * 8),
                autoRenew: false
            ),
            Ad(
                id: UUID(),
                title: "Smart Home Starter Kit",
                description: "Bundle of smart bulbs, plugs, and voice assistant speaker.",
                price: 299.99,
                category: "Electronics",
                location: "Remote",
                status: .draft,
                platforms: [],
                totalPosts: 0,
                totalViews: 0,
                totalLeads: 0,
                createdAt: now.addingTimeInterval(-86400),
                scheduledTime: nil,
                autoRenew: false
            )
        ]
        
        platforms = [
            PlatformAccount(name: "Facebook Marketplace", username: "@crosspostme", status: .connected, lastSync: now.addingTimeInterval(-1800)),
            PlatformAccount(name: "Etsy", username: "@crosspostme.design", status: .needsAttention, lastSync: now.addingTimeInterval(-7200)),
            PlatformAccount(name: "Craigslist", username: "Austin Listings", status: .connected, lastSync: now.addingTimeInterval(-600)),
            PlatformAccount(name: "eBay", username: "CrossPostHQ", status: .notConnected, lastSync: nil)
        ]
        
        messages = [
            LeadMessage(sender: "Alex Johnson", platform: "Facebook", preview: "Is the road bike still available?", receivedAt: now.addingTimeInterval(-900)),
            LeadMessage(sender: "Jamie from Denver", platform: "Etsy", preview: "Can you share more photos of the desk?", receivedAt: now.addingTimeInterval(-3600)),
            LeadMessage(sender: "Mia", platform: "Craigslist", preview: "I'd like to schedule a pickup this weekend.", receivedAt: now.addingTimeInterval(-10800))
        ]
    }
}
