import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { buildSpotifyAuthorizeUrl, spotifyDefaultScopes } from "../providers/spotifyAuth.js";

const providerSchema = z.enum(["apple_music", "spotify"]);

const connectProviderSchema = z.object({
  provider: providerSchema,
  providerUserId: z.string().min(1),
  scopes: z.array(z.string()).default([])
});

const spotifyAuthorizeSchema = z.object({
  codeChallenge: z.string().min(32),
  state: z.string().min(16),
  scopes: z.array(z.string()).optional()
});

export async function registerAuthRoutes(server: FastifyInstance) {
  server.get("/auth/providers", async () => ({
    data: [
      {
        provider: "apple_music",
        displayName: "Apple Music",
        status: "planned",
        notes: "Use MusicKit authorization on iOS and server-generated developer tokens."
      },
      {
        provider: "spotify",
        displayName: "Spotify",
        status: "planned",
        notes: "Use OAuth Authorization Code with PKCE for mobile clients."
      }
    ]
  }));

  server.post("/auth/provider-connections", async (request, reply) => {
    const parsed = connectProviderSchema.safeParse(request.body);

    if (!parsed.success) {
      return reply.code(400).send({
        error: "invalid_request",
        issues: parsed.error.issues
      });
    }

    return reply.code(202).send({
      data: {
        id: crypto.randomUUID(),
        ...parsed.data,
        connectedAt: new Date().toISOString()
      }
    });
  });

  server.post("/auth/spotify/authorize-url", async (request, reply) => {
    const parsed = spotifyAuthorizeSchema.safeParse(request.body);

    if (!parsed.success) {
      return reply.code(400).send({
        error: "invalid_request",
        issues: parsed.error.issues
      });
    }

    try {
      return {
        data: {
          url: buildSpotifyAuthorizeUrl(parsed.data),
          scopes: parsed.data.scopes ?? spotifyDefaultScopes
        }
      };
    } catch (error) {
      request.log.error(error);

      return reply.code(500).send({
        error: "spotify_auth_not_configured"
      });
    }
  });
}
