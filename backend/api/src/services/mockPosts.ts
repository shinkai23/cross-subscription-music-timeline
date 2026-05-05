export const mockPosts = [
  {
    id: "post_late_night_walk",
    author: {
      id: "user_aki",
      displayName: "Aki",
      handle: "aki"
    },
    itemType: "playlist",
    sourceProvider: "spotify",
    sourceItemId: "spotify_playlist_late_night_walk",
    title: "Late Night Walk",
    subtitle: "18 tracks",
    caption: "Quiet tracks for walking home after the last train.",
    tags: ["night", "walk", "calm"],
    matchSummary: {
      targetProvider: "apple_music",
      matchedCount: 16,
      totalCount: 18,
      needsReviewCount: 2
    },
    createdAt: new Date().toISOString()
  }
];

