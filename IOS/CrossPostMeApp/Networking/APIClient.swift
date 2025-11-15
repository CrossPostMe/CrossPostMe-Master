import Foundation

protocol APIRequestPerforming {
    func perform<T: Decodable>(_ request: URLRequest, decoding type: T.Type) async throws -> T
    func perform(_ request: URLRequest) async throws
}

final class APIClient: APIRequestPerforming {
    private let session: URLSession
    private let logger: NetworkLogger

    init(session: URLSession = .shared, logger: NetworkLogger = .init()) {
        self.session = session
        self.logger = logger
    }

    func perform<T>(_ request: URLRequest, decoding type: T.Type) async throws -> T where T: Decodable {
        let data = try await performRequest(request)
        do {
            return try JSONDecoder.iso8601.decode(T.self, from: data)
        } catch {
            logger.log(.error, "Decoding failed: \(error)")
            throw APIError.decodingFailed
        }
    }

    func perform(_ request: URLRequest) async throws {
        _ = try await performRequest(request)
    }

    private func performRequest(_ request: URLRequest) async throws -> Data {
        logger.log(.info, "➡️ \(request.httpMethod ?? "") \(request.url?.absoluteString ?? "")")
        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.unknown
            }
            guard 200..<300 ~= httpResponse.statusCode else {
                if httpResponse.statusCode == 401 { throw APIError.unauthorized }
                throw APIError.serverError(httpResponse.statusCode)
            }
            return data
        } catch {
            throw APIError.transport(error)
        }
    }
}

// MARK: - Helpers

extension URLRequest {
    static func apiRequest(endpoint: APIEndpoint,
                           method: String,
                           body: Encodable? = nil,
                           authToken: String? = nil) throws -> URLRequest {
        let baseURL = AppConfig.current.apiBaseURL
        guard let url = URL(string: endpoint.path, relativeTo: baseURL) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let authToken {
            request.setValue("Bearer \(authToken)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            do {
                request.httpBody = try JSONEncoder.iso8601.encode(body)
            } catch {
                throw APIError.encodingFailed
            }
        }
        return request
    }
}

final class NetworkLogger {
    enum Level { case info, error }

    func log(_ level: Level, _ message: String) {
        guard AppConfig.current.enableVerboseLogging else { return }
        print("[Network] \(level): \(message)")
    }
}

extension JSONDecoder {
    static let iso8601: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
}

extension JSONEncoder {
    static let iso8601: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        return encoder
    }()
}
