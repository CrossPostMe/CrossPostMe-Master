import XCTest
@testable import CrossPostMeApp

final class AppConfigTests: XCTestCase {
    func testConfigLoadsFromBundle() throws {
        let config = AppConfig.current
        XCTAssertFalse(config.apiBaseURL.absoluteString.isEmpty)
    }
}
