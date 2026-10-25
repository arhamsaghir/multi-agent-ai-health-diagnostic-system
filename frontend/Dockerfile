# AegisMed frontend image — Next.js 16 clinical portal
#
# Build:  docker build -t aegismed-frontend frontend/
# Run:    docker run --rm -p 3000:3000 aegismed-frontend
#
# The browser talks to the backend through the /api/backend proxy route
# (same-origin), so no CORS configuration is needed on the hospital LAN.
# NEXT_PUBLIC_API_URL is inlined at build time, exactly like a Vercel build.

FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Default to the same-origin proxy route; override at build time to point
# the browser straight at a backend (e.g. http://localhost:8000).
ARG NEXT_PUBLIC_API_URL=/api/backend
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 10001 nodejs \
    && adduser --system --uid 10001 nextjs

# `output: "standalone"` emits a self-contained server with only the
# traced node_modules, plus the static assets copied alongside it.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["node", "server.js"]
