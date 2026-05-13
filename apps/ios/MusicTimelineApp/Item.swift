//
//  Item.swift
//  MusicTimelineApp
//
//  Created by Sinkai I on 2026/05/06.
//

import Foundation
import SwiftData

enum MusicPostType: String, Codable, CaseIterable {
    case track
    case album
    case playlist
}

@Model
final class Item {
    var serviceName: String
    var postType: MusicPostType
    var title: String
    var creatorName: String
    var posterName: String
    var metadataLine: String
    var caption: String
    var tags: [String]
    var isFromFollowing: Bool
    var isNewRelease: Bool
    var isLikedByUser: Bool
    var isSavedByUser: Bool
    var isOwnedByCurrentUser: Bool
    var playedAt: Date
    var likeCount: Int
    var saveCount: Int
    var commentCount: Int
    var repostCount: Int
    var shareCount: Int

    init(
        serviceName: String,
        postType: MusicPostType,
        title: String,
        creatorName: String,
        posterName: String,
        metadataLine: String,
        caption: String,
        tags: [String],
        isFromFollowing: Bool,
        isNewRelease: Bool,
        isLikedByUser: Bool,
        isSavedByUser: Bool,
        isOwnedByCurrentUser: Bool,
        playedAt: Date,
        likeCount: Int,
        saveCount: Int,
        commentCount: Int,
        repostCount: Int,
        shareCount: Int
    ) {
        self.serviceName = serviceName
        self.postType = postType
        self.title = title
        self.creatorName = creatorName
        self.posterName = posterName
        self.metadataLine = metadataLine
        self.caption = caption
        self.tags = tags
        self.isFromFollowing = isFromFollowing
        self.isNewRelease = isNewRelease
        self.isLikedByUser = isLikedByUser
        self.isSavedByUser = isSavedByUser
        self.isOwnedByCurrentUser = isOwnedByCurrentUser
        self.playedAt = playedAt
        self.likeCount = likeCount
        self.saveCount = saveCount
        self.commentCount = commentCount
        self.repostCount = repostCount
        self.shareCount = shareCount
    }
}

extension Item {
    var searchableStrings: [String] {
        [
            title,
            creatorName,
            posterName,
            serviceName,
            metadataLine,
            caption,
            postType.rawValue,
            viralContextLine
        ] + tags
    }

    var viralContextLine: String {
        if isNewRelease && saveCount >= 120 {
            return "Save spike"
        }
        if repostCount >= 40 {
            return "Passing through group chats"
        }
        if isFromFollowing && likeCount >= 180 {
            return "Your circle is pushing this"
        }
        if postType == .playlist {
            return "Playlist people keep reopening"
        }
        return "Quiet momentum"
    }

    static var sampleTimeline: [Item] {
        [
            Item(
                serviceName: "Spotify",
                postType: .track,
                title: "Nights",
                creatorName: "Frank Ocean",
                posterName: "@midnightloop",
                metadataLine: "Track • Blonde",
                caption: "Late-night commute track. The beat switch still lands every time.",
                tags: ["late-night", "drive", "frank-ocean"],
                isFromFollowing: true,
                isNewRelease: false,
                isLikedByUser: true,
                isSavedByUser: true,
                isOwnedByCurrentUser: false,
                playedAt: Calendar.current.date(byAdding: .minute, value: -12, to: .now) ?? .now,
                likeCount: 284,
                saveCount: 91,
                commentCount: 32,
                repostCount: 14,
                shareCount: 18
            ),
            Item(
                serviceName: "Apple Music",
                postType: .album,
                title: "Ctrl",
                creatorName: "SZA",
                posterName: "@rnbarchive",
                metadataLine: "Album • 14 tracks",
                caption: "Running the whole album front to back. No skips today.",
                tags: ["album-run", "rnb", "sza"],
                isFromFollowing: true,
                isNewRelease: false,
                isLikedByUser: false,
                isSavedByUser: true,
                isOwnedByCurrentUser: false,
                playedAt: Calendar.current.date(byAdding: .hour, value: -2, to: .now) ?? .now,
                likeCount: 412,
                saveCount: 137,
                commentCount: 46,
                repostCount: 21,
                shareCount: 26
            ),
            Item(
                serviceName: "YouTube Music",
                postType: .playlist,
                title: "Tokyo Night Ride",
                creatorName: "Sinkai I",
                posterName: "@sinkaii",
                metadataLine: "Playlist • 27 saves",
                caption: "Built a neon drive playlist with sharp transitions and no dead air.",
                tags: ["playlist", "city-pop", "night-drive"],
                isFromFollowing: false,
                isNewRelease: false,
                isLikedByUser: true,
                isSavedByUser: false,
                isOwnedByCurrentUser: true,
                playedAt: Calendar.current.date(byAdding: .hour, value: -5, to: .now) ?? .now,
                likeCount: 153,
                saveCount: 74,
                commentCount: 12,
                repostCount: 9,
                shareCount: 11
            ),
            Item(
                serviceName: "Spotify",
                postType: .track,
                title: "Saturn",
                creatorName: "SZA",
                posterName: "@newmusicdaily",
                metadataLine: "Track • New Release",
                caption: "Fresh drop. This one is already taking over the feed.",
                tags: ["new", "sza", "fresh"],
                isFromFollowing: false,
                isNewRelease: true,
                isLikedByUser: false,
                isSavedByUser: false,
                isOwnedByCurrentUser: false,
                playedAt: Calendar.current.date(byAdding: .minute, value: -35, to: .now) ?? .now,
                likeCount: 521,
                saveCount: 204,
                commentCount: 88,
                repostCount: 54,
                shareCount: 48
            ),
            Item(
                serviceName: "Apple Music",
                postType: .playlist,
                title: "Summer Rotation",
                creatorName: "Editorial Team",
                posterName: "@playlistclub",
                metadataLine: "Playlist • Recommended For You",
                caption: "A tighter pop and alt mix based on your saves this week.",
                tags: ["recommended", "summer", "pop"],
                isFromFollowing: true,
                isNewRelease: true,
                isLikedByUser: false,
                isSavedByUser: true,
                isOwnedByCurrentUser: false,
                playedAt: Calendar.current.date(byAdding: .hour, value: -8, to: .now) ?? .now,
                likeCount: 302,
                saveCount: 144,
                commentCount: 28,
                repostCount: 17,
                shareCount: 22
            )
        ]
    }

    static func demoPost(at date: Date) -> Item {
        let demos: [Item] = [
            Item(
                serviceName: "Spotify",
                postType: .track,
                title: "After Hours",
                creatorName: "The Weeknd",
                posterName: "@nightshift",
                metadataLine: "Track • After Hours",
                caption: "Synths on, notifications off.",
                tags: ["synth", "night", "the-weeknd"],
                isFromFollowing: true,
                isNewRelease: false,
                isLikedByUser: false,
                isSavedByUser: false,
                isOwnedByCurrentUser: false,
                playedAt: date,
                likeCount: 198,
                saveCount: 53,
                commentCount: 17,
                repostCount: 8,
                shareCount: 9
            ),
            Item(
                serviceName: "Apple Music",
                postType: .album,
                title: "Channel Orange",
                creatorName: "Frank Ocean",
                posterName: "@albumtalk",
                metadataLine: "Album • 17 tracks",
                caption: "Replaying the full record changes the pace of the afternoon.",
                tags: ["album", "frank-ocean", "classic"],
                isFromFollowing: false,
                isNewRelease: false,
                isLikedByUser: true,
                isSavedByUser: true,
                isOwnedByCurrentUser: false,
                playedAt: date,
                likeCount: 337,
                saveCount: 126,
                commentCount: 34,
                repostCount: 16,
                shareCount: 19
            ),
            Item(
                serviceName: "YouTube Music",
                postType: .playlist,
                title: "Sunday Reset",
                creatorName: "Home Feed",
                posterName: "@homeroom",
                metadataLine: "Playlist • 42 tracks",
                caption: "This queue keeps the room moving without demanding attention.",
                tags: ["playlist", "reset", "weekend"],
                isFromFollowing: true,
                isNewRelease: true,
                isLikedByUser: false,
                isSavedByUser: false,
                isOwnedByCurrentUser: true,
                playedAt: date,
                likeCount: 121,
                saveCount: 67,
                commentCount: 10,
                repostCount: 7,
                shareCount: 14
            )
        ]

        return demos.randomElement() ?? demos[0]
    }
}
