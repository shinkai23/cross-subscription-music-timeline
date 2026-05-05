import type { FastifyInstance } from "fastify";
import { z } from "zod";

const providerSchema = z.enum(["apple_music", "spotify"]);

const connectProviderSchema = z.object({
  provider: providerSchema,
  providerUserId: z.string().min(1),
  scopes: z.array(z.string()).default([])
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
}
