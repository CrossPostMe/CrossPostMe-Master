import Foundation

enum AppConfig {
    private static var cached: Configuration?

    static var current: Configuration {
        if let cached {
            return cached
        }

        guard let url = Bundle.main.url(forResource: "Config", withExtension: "plist"),
              let data = try? Data(contentsOf: url) else {
            fatalError("Config.plist is missing from the main bundle")
        }

        do {
            let decoder = PropertyListDecoder()
            let configuration = try decoder.decode(Configuration.self, from: data)
            cached = configuration
            return configuration
        } catch {
            fatalError("Failed to decode Config.plist: \(error)")
        }
    }

    struct Configuration: Codable {
        let apiBaseURL: URL
        let enableVerboseLogging: Bool
    }
}
