import type { ProviderPlaylist, ProviderTrack } from "../domain/music.js";

export type TrackSearchQuery = {
  title?: string;
  artist?: string;
  isrc?: string;
};

export type CreatePlaylistInput = {
  name: string;
  description?: string;
  tracks: ProviderTrack[];
};

export interface MusicProviderAdapter {
  searchTracks(query: TrackSearchQuery, userToken?: string): Promise<ProviderTrack[]>;
  getPlaylist(id: string, userToken?: string): Promise<ProviderPlaylist>;
  createPlaylist(input: CreatePlaylistInput, userToken: string): Promise<{ id: string; url: string }>;
  buildOpenUrl(providerItemId: string): string;
}

