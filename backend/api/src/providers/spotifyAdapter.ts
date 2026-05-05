import type { ProviderPlaylist, ProviderTrack } from "../domain/music.js";
import type { CreatePlaylistInput, MusicProviderAdapter, TrackSearchQuery } from "./MusicProviderAdapter.js";

export class SpotifyAdapter implements MusicProviderAdapter {
  async searchTracks(_query: TrackSearchQuery, _userToken?: string): Promise<ProviderTrack[]> {
    throw new Error("Spotify search is not implemented yet");
  }

  async getPlaylist(_id: string, _userToken?: string): Promise<ProviderPlaylist> {
    throw new Error("Spotify playlist loading is not implemented yet");
  }

  async createPlaylist(_input: CreatePlaylistInput, _userToken: string): Promise<{ id: string; url: string }> {
    throw new Error("Spotify playlist creation is not implemented yet");
  }

  buildOpenUrl(providerItemId: string): string {
    return `https://open.spotify.com/${encodeURIComponent(providerItemId)}`;
  }
}

