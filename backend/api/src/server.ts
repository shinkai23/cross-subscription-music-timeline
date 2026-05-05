import cors from "@fastify/cors";
import Fastify from "fastify";
import { registerHealthRoutes } from "./routes/health.js";
import { registerPostRoutes } from "./routes/posts.js";

const server = Fastify({
  logger: true
});

await server.register(cors, {
  origin: true
});

await registerHealthRoutes(server);
await registerPostRoutes(server);

const port = Number(process.env.PORT ?? 4000);
const host = process.env.HOST ?? "127.0.0.1";

try {
  await server.listen({ port, host });
} catch (error) {
  server.log.error(error);
  process.exit(1);
}

