//
//  TimelineView.swift
//  MusicTimelineApp
//

import SwiftUI

struct TimelineView: View {
    var apiClient: APIClient = .shared
    var refreshTrigger: Int = 0
    var onMetricsChange: ((CGFloat) -> Void)? = nil

    @State private var posts: [PostDTO] = []
    @State private var isLoading = false
    @State private var isShowingTrackSearch = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 14) {
                    if isLoading && posts.isEmpty {
                        ProgressView()
                            .frame(maxWidth: .infinity)
                            .padding(.top, 40)
                    } else if let errorMessage, posts.isEmpty {
                        errorState(errorMessage)
                    } else if posts.isEmpty {
                        emptyState
                    } else {
                        ForEach(posts) { post in
                            PostCardView(post: post)
                        }
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 12)
                .padding(.bottom, 96)
            }
            .navigationTitle("Music Timeline")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        isShowingTrackSearch = true
                    } label: {
                        Image(systemName: "plus")
                    }
                    .accessibilityLabel("Create post")
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        Task {
                            await loadTimeline()
                        }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                    .disabled(isLoading)
                }
            }
            .refreshable {
                await loadTimeline()
            }
        }
        .task {
            await loadTimeline()
        }
        .onChange(of: refreshTrigger) {
            Task {
                await loadTimeline()
            }
        }
        .onAppear {
            onMetricsChange?(0)
        }
        .sheet(isPresented: $isShowingTrackSearch) {
            TrackSearchView(apiClient: apiClient) { _ in
                Task {
                    await loadTimeline()
                }
            }
        }
    }

    @ViewBuilder
    private func errorState(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Unable to load posts")
                .font(.headline)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Button {
                Task {
                    await loadTimeline()
                }
            } label: {
                Label("Retry", systemImage: "arrow.clockwise")
            }
            .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
    }

    private var emptyState: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("No posts yet")
                .font(.headline)
            Text("Search for a track, add a caption, and create the first post.")
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Button {
                isShowingTrackSearch = true
            } label: {
                Label("Create Post", systemImage: "plus")
            }
            .buttonStyle(.borderedProminent)
            .padding(.top, 6)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 8))
    }

    @MainActor
    private func loadTimeline() async {
        guard !isLoading else { return }
        isLoading = true
        errorMessage = nil

        do {
            posts = try await apiClient.fetchTimeline().items
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

#Preview("Timeline API") {
    TimelinePreviewContainer()
}

private struct TimelinePreviewContainer: View {
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 14) {
                ForEach(TimelineResponse.preview.items) { post in
                    PostCardView(post: post)
                }
            }
            .padding()
        }
    }
}
