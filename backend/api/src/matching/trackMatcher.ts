import type { ProviderTrack, TrackMatch } from "../domain/music.js";

export function matchTracks(sourceTracks: ProviderTrack[], targetTracks: ProviderTrack[]): TrackMatch[] {
  return sourceTracks.map((source) => {
    const byIsrc = source.isrc
      ? targetTracks.find((target) => target.isrc && target.isrc === source.isrc)
      : undefined;

    if (byIsrc) {
      return {
        source,
        target: byIsrc,
        confidence: 1,
        reason: "isrc"
      };
    }

    const byTitleArtistAlbum = targetTracks.find((target) =>
      normalize(target.title) === normalize(source.title) &&
      normalize(target.artistName) === normalize(source.artistName) &&
      normalize(target.albumName ?? "") === normalize(source.albumName ?? "")
    );

    if (byTitleArtistAlbum) {
      return {
        source,
        target: byTitleArtistAlbum,
        confidence: 0.9,
        reason: "title_artist_album"
      };
    }

    const byTitleArtistDuration = targetTracks.find((target) =>
      normalize(target.title) === normalize(source.title) &&
      normalize(target.artistName) === normalize(source.artistName) &&
      isDurationClose(source.durationMs, target.durationMs)
    );

    if (byTitleArtistDuration) {
      return {
        source,
        target: byTitleArtistDuration,
        confidence: 0.78,
        reason: "title_artist_duration"
      };
    }

    return {
      source,
      confidence: 0,
      reason: "unavailable"
    };
  });
}

function normalize(value: string): string {
  return value
    .toLocaleLowerCase("en-US")
    .replace(/\s+\([^)]*\)/g, "")
    .replace(/\s+-\s+(remaster(ed)?|live|radio edit).*$/i, "")
    .replace(/\s+/g, " ")
    .trim();
}

function isDurationClose(source?: number, target?: number): boolean {
  if (!source || !target) {
    return false;
  }

  return Math.abs(source - target) <= 4_000;
}

