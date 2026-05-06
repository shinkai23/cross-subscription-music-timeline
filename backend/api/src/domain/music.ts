export type MusicProvider = "apple_music" | "spotify";
export type MusicItemType = "song" | "album" | "playlist";

export type ProviderTrack = {
  provider: MusicProvider;
  providerTrackId: string;
  isrc?: string;
  title: string;
  artistName: string;
  albumName?: string;
  durationMs?: number;
  artworkUrl?: string;
  providerUrl: string;
};

export type ProviderPlaylist = {
  provider: MusicProvider;
  providerPlaylistId: string;
  title: string;
  description?: string;
  ownerDisplayName?: string;
  providerUrl: string;
  tracks: ProviderTrack[];
};

export type TrackMatch = {
  source: ProviderTrack;
  target?: ProviderTrack;
  confidence: number;
  reason: "isrc" | "title_artist_album" | "title_artist_duration" | "candidate_review" | "unavailable";
};

