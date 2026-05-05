import { describe, expect, it } from "vitest";
import type { ProviderTrack } from "../domain/music.js";
import { matchTracks } from "./trackMatcher.js";

function track(overrides: Partial<ProviderTrack>): ProviderTrack {
  return {
    provider: "spotify",
    providerTrackId: crypto.randomUUID(),
    title: "Cloud 9",
    artistName: "Beach Bunny",
    albumName: "Blame Game",
    durationMs: 147_000,
    providerUrl: "https://example.com",
    ...overrides
  };
}

describe("matchTracks", () => {
  it("prefers exact ISRC matches", () => {
    const source = track({ provider: "spotify", providerTrackId: "source", isrc: "USQE91600054" });
    const target = track({ provider: "apple_music", providerTrackId: "target", isrc: "USQE91600054" });

    const [match] = matchTracks([source], [target]);

    expect(match.target?.providerTrackId).toBe("target");
    expect(match.confidence).toBe(1);
    expect(match.reason).toBe("isrc");
  });

  it("falls back to title, artist, and album", () => {
    const source = track({ provider: "spotify", providerTrackId: "source", isrc: undefined });
    const target = track({ provider: "apple_music", providerTrackId: "target", isrc: undefined });

    const [match] = matchTracks([source], [target]);

    expect(match.target?.providerTrackId).toBe("target");
    expect(match.reason).toBe("title_artist_album");
  });

  it("marks unavailable tracks when no match is found", () => {
    const source = track({ providerTrackId: "source", title: "Missing Track" });
    const target = track({ providerTrackId: "target", title: "Different Track" });

    const [match] = matchTracks([source], [target]);

    expect(match.target).toBeUndefined();
    expect(match.reason).toBe("unavailable");
  });
});
