import type { FastifyInstance } from "fastify";
import { z } from "zod";
import { mockPosts } from "../services/mockPosts.js";

const createPostSchema = z.object({
  itemType: z.enum(["song", "album", "playlist"]),
  sourceProvider: z.enum(["apple_music", "spotify"]),
  sourceItemId: z.string().min(1),
  caption: z.string().max(500),
  visibility: z.enum(["public", "followers", "private"]).default("public")
});

export async function registerPostRoutes(server: FastifyInstance) {
  server.get("/posts", async () => ({
    data: mockPosts
  }));

  server.post("/posts", async (request, reply) => {
    const parsed = createPostSchema.safeParse(request.body);

    if (!parsed.success) {
      return reply.code(400).send({
        error: "invalid_request",
        issues: parsed.error.issues
      });
    }

    return reply.code(201).send({
      data: {
        id: crypto.randomUUID(),
        ...parsed.data,
        createdAt: new Date().toISOString()
      }
    });
  });
}

