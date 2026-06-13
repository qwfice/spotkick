import SwiftUI

// MARK: - Data Models
struct PenaltyPrediction: Codable, Identifiable {
    let id = UUID()
    let player_name: String
    let country: String
    let overall_conversion_rate: Double
    let predicted_score_probability: Double
    let confidence: String
    let total_penalties: Int
    let shootout_conversion_rate: Double
    let favorite_direction: String
    let ai_insight: String
    let key_factors: [String]
    let direction_breakdown: DirectionBreakdown
    let context_analysis: ContextAnalysis
    let recent_form: [RecentForm]

    struct DirectionBreakdown: Codable {
        let left: DirectionStat
        let right: DirectionStat
        let center: DirectionStat
    }

    struct DirectionStat: Codable {
        let scored: Int
        let missed: Int
        let total: Int
        let rate: Double
    }

    struct ContextAnalysis: Codable {
        let context: String
        let context_rate: Double
        let context_total: Int
    }

    struct RecentForm: Codable {
        let result: String
        let direction: String
        let context: String
        let competition: String
        let date: String
    }
}

// MARK: - API Service
class SpotKickAPI: ObservableObject {
    static let shared = SpotKickAPI()
    private let baseURL = "http://localhost:8000" // Change to deployed URL

    func predict(player: String, context: String) async throws -> PenaltyPrediction {
        let encodedPlayer = player.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed)!
        let url = URL(string: "\(baseURL)/predict/\(encodedPlayer)?context=\(context)")!

        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(PenaltyPrediction.self, from: data)
    }

    func search(query: String) async throws -> SearchResponse {
        let encoded = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!
        let url = URL(string: "\(baseURL)/search?q=\(encoded)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(SearchResponse.self, from: data)
    }
}

struct SearchResponse: Codable {
    let query: String
    let results: [PlayerSearchResult]
}

struct PlayerSearchResult: Codable, Identifiable {
    let id = UUID()
    let name: String
    let country: String
    let conversion_rate: Double
    let total: Int
}

// MARK: - Main App
@main
struct SpotKickApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

// MARK: - Content View
struct ContentView: View {
    @StateObject private var viewModel = ChatViewModel()

    var body: some View {
        NavigationView {
            ChatView(viewModel: viewModel)
                .navigationTitle("SpotKick")
                .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// MARK: - Chat View Model
class ChatViewModel: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var inputText = ""
    @Published var isLoading = false
    @Published var selectedContext = "knockout"

    let contexts = [
        ("knockout", "Knockout"),
        ("shootout", "Shootout"),
        ("group_stage", "Group Stage"),
        ("league", "League"),
        ("cup", "Cup")
    ]

    init() {
        addWelcomeMessage()
    }

    func addWelcomeMessage() {
        messages.append(ChatMessage(
            text: "Welcome to SpotKick. Type any player's name and I'll predict their penalty success rate based on their entire career history.",
            isUser: false
        ))
    }

    func sendMessage() {
        guard !inputText.isEmpty else { return }
        let text = inputText
        inputText = ""

        messages.append(ChatMessage(text: text, isUser: true))
        isLoading = true

        Task {
            do {
                let prediction = try await SpotKickAPI.shared.predict(player: text, context: selectedContext)
                await MainActor.run {
                    messages.append(ChatMessage(prediction: prediction, isUser: false))
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    messages.append(ChatMessage(text: "Could not find player or connect to server.", isUser: false))
                    isLoading = false
                }
            }
        }
    }
}

// MARK: - Chat Message Model
struct ChatMessage: Identifiable {
    let id = UUID()
    let text: String?
    let prediction: PenaltyPrediction?
    let isUser: Bool
    let timestamp = Date()

    init(text: String, isUser: Bool) {
        self.text = text
        self.prediction = nil
        self.isUser = isUser
    }

    init(prediction: PenaltyPrediction, isUser: Bool) {
        self.text = nil
        self.prediction = prediction
        self.isUser = isUser
    }
}

// MARK: - Chat View
struct ChatView: View {
    @ObservedObject var viewModel: ChatViewModel

    var body: some View {
        VStack(spacing: 0) {
            // Context selector
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(viewModel.contexts, id: \.0) { context, label in
                        ContextChip(
                            label: label,
                            isSelected: viewModel.selectedContext == context
                        ) {
                            viewModel.selectedContext = context
                        }
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 8)
            }
            .background(Color(.systemGray6))

            // Messages
            ScrollView {
                LazyVStack(spacing: 12) {
                    ForEach(viewModel.messages) { message in
                        MessageBubble(message: message)
                    }
                    if viewModel.isLoading {
                        TypingIndicator()
                    }
                }
                .padding()
            }

            // Input
            HStack(spacing: 12) {
                TextField("Type a player name...", text: $viewModel.inputText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .submitLabel(.send)
                    .onSubmit { viewModel.sendMessage() }

                Button(action: viewModel.sendMessage) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 32))
                        .foregroundColor(.green)
                }
                .disabled(viewModel.inputText.isEmpty || viewModel.isLoading)
            }
            .padding()
            .background(Color(.systemBackground))
        }
    }
}

// MARK: - Message Bubble
struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.isUser { Spacer() }

            if let prediction = message.prediction {
                PredictionCard(prediction: prediction)
            } else if let text = message.text {
                Text(text)
                    .padding(12)
                    .background(message.isUser ? Color.green : Color(.systemGray5))
                    .foregroundColor(message.isUser ? .white : .primary)
                    .cornerRadius(18)
            }

            if !message.isUser { Spacer() }
        }
    }
}

// MARK: - Prediction Card
struct PredictionCard: View {
    let prediction: PenaltyPrediction

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(prediction.player_name)
                        .font(.headline)
                    Text(prediction.country)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                Spacer()
                Text("\(prediction.total_penalties) pens")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            // Big Number
            VStack(spacing: 4) {
                Text("\(String(format: "%.1f", prediction.predicted_score_probability))%")
                    .font(.system(size: 56, weight: .bold, design: .rounded))
                    .foregroundColor(.green)
                Text("Predicted Score Probability")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)

            // Confidence Badge
            HStack {
                Text(prediction.confidence)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(confidenceColor.opacity(0.15))
                    .foregroundColor(confidenceColor)
                    .cornerRadius(20)
                Spacer()
            }

            // AI Insight
            Text(prediction.ai_insight)
                .font(.subheadline)
                .padding(12)
                .background(Color.green.opacity(0.05))
                .cornerRadius(8)

            // Stats Grid
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                StatBox(value: "\(String(format: "%.1f", prediction.overall_conversion_rate))%", label: "Career Rate")
                StatBox(value: "\(String(format: "%.1f", prediction.shootout_conversion_rate))%", label: "Shootout Rate")
                StatBox(value: "\(String(format: "%.1f", prediction.context_analysis.context_rate))%", label: prediction.context_analysis.context.replacingOccurrences(of: "_", with: " ").capitalized)
                StatBox(value: prediction.favorite_direction.capitalized, label: "Favorite Side")
            }

            // Direction Bars
            VStack(alignment: .leading, spacing: 8) {
                Text("Direction Breakdown")
                    .font(.caption)
                    .foregroundColor(.secondary)
                DirectionBar(label: "Left", rate: prediction.direction_breakdown.left.rate)
                DirectionBar(label: "Right", rate: prediction.direction_breakdown.right.rate)
                DirectionBar(label: "Center", rate: prediction.direction_breakdown.center.rate)
            }
        }
        .padding(16)
        .background(Color(.systemGray6))
        .cornerRadius(16)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    var confidenceColor: Color {
        if prediction.confidence.lowercased().contains("high") { return .green }
        if prediction.confidence.lowercased().contains("medium") { return .orange }
        return .red
    }
}

struct StatBox: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundColor(.green)
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(10)
        .background(Color(.systemBackground))
        .cornerRadius(8)
    }
}

struct DirectionBar: View {
    let label: String
    let rate: Double

    var body: some View {
        HStack {
            Text(label)
                .font(.caption)
                .frame(width: 50, alignment: .leading)
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color(.systemGray4))
                        .cornerRadius(4)
                    Rectangle()
                        .fill(Color.green)
                        .frame(width: geo.size.width * CGFloat(rate / 100))
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)
            Text("\(String(format: "%.0f", rate))%")
                .font(.caption)
                .frame(width: 40, alignment: .trailing)
        }
    }
}

struct ContextChip: View {
    let label: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(label)
                .font(.subheadline)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.green : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

struct TypingIndicator: View {
    @State private var offset: CGFloat = 0

    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { i in
                    Circle()
                        .fill(Color.secondary)
                        .frame(width: 6, height: 6)
                        .offset(y: offset)
                        .animation(
                            Animation.easeInOut(duration: 0.5)
                                .repeatForever()
                                .delay(Double(i) * 0.2),
                            value: offset
                        )
                }
            }
            .padding(12)
            .background(Color(.systemGray5))
            .cornerRadius(18)
            Spacer()
        }
        .onAppear { offset = -4 }
    }
}
