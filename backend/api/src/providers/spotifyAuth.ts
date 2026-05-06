import { z } from "zod";

const spotifyAuthConfigSchema = z.object({
  clientId: z.string().min(1),
  redirectUri: z.string().url()
});

export type SpotifyAuthorizeInput = {
  codeChallenge: string;
  state: string;
  scopes?: string[];
};

const defaultScopes = [
  "playlist-read-private",
  "playlist-modify-private",
  "playlist-modify-public"
];

export function buildSpotifyAuthorizeUrl(input: SpotifyAuthorizeInput): string {
  const config = spotifyAuthConfigSchema.parse({
    clientId: process.env.SPOTIFY_CLIENT_ID,
    redirectUri: process.env.SPOTIFY_REDIRECT_URI
  });

  const url = new URL("https://accounts.spotify.com/authorize");
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", config.clientId);
  url.searchParams.set("redirect_uri", config.redirectUri);
  url.searchParams.set("code_challenge_method", "S256");
  url.searchParams.set("code_challenge", input.codeChallenge);
  url.searchParams.set("state", input.state);
  url.searchParams.set("scope", (input.scopes ?? defaultScopes).join(" "));

  return url.toString();
}

export const spotifyDefaultScopes = defaultScopes;

