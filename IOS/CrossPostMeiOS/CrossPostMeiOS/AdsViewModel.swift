import Foundation

@MainActor
final class AdsViewModel: ObservableObject {
    @Published private(set) var ads: [Ad]
    @Published private(set) var dashboardStats: DashboardStats
    @Published private(set) var platforms: [PlatformAccount]
    @Published private(set) var messages: [LeadMessage]
    
    init(mockData: MockData = .shared) {
        self.ads = mockData.ads
        self.platforms = mockData.platforms
        self.messages = mockData.messages
        self.dashboardStats = AdsViewModel.makeStats(for: mockData.ads, platforms: mockData.platforms)
    }
    
    func createAd(title: String, description: String, price: Double, category: String, location: String, autoRenew: Bool) {
        let newAd = Ad(
            id: UUID(),
            title: title,
            description: description,
            price: price,
            category: category,
            location: location,
            status: .draft,
            platforms: [],
            totalPosts: 0,
            totalViews: 0,
            totalLeads: 0,
            createdAt: Date(),
            scheduledTime: nil,
            autoRenew: autoRenew
        )
        ads.insert(newAd, at: 0)
        dashboardStats = AdsViewModel.makeStats(for: ads, platforms: platforms)
    }
    
    func updatePlatformStatus(_ platform: PlatformAccount, to status: PlatformAccount.Status) {
        guard let index = platforms.firstIndex(where: { $0.id == platform.id }) else { return }
        platforms[index].status = status
        platforms[index].lastSync = Date()
        dashboardStats = AdsViewModel.makeStats(for: ads, platforms: platforms)
    }
    
    private static func makeStats(for ads: [Ad], platforms: [PlatformAccount]) -> DashboardStats {
        let activeAds = ads.filter { $0.status == .active }.count
        let totalPosts = ads.reduce(0) { $0 + $1.totalPosts }
        let totalViews = ads.reduce(0) { $0 + $1.totalViews }
        let totalLeads = ads.reduce(0) { $0 + $1.totalLeads }
        let connectedPlatforms = platforms.filter { $0.status == .connected }.count
        
        return DashboardStats(
            totalAds: ads.count,
            activeAds: activeAds,
            platformsConnected: connectedPlatforms,
            totalPosts: totalPosts,
            totalViews: totalViews,
            totalLeads: totalLeads
        )
    }
}
