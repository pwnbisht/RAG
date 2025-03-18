# Stage 1: Build the Next.js application
# FROM node:18-alpine AS builder

# WORKDIR /app
# COPY package*.json ./
# RUN npm install
# COPY . .
# RUN npm run build

# # Stage 2: Serve the application
# FROM node:18-alpine

# WORKDIR /app
# ENV NODE_ENV=production
# COPY --from=builder /.next ./.next
# COPY --from=builder /public ./public
# COPY --from=builder /package*.json ./
# COPY --from=builder /next.config.mjs ./
# COPY --from=builder /src ./src

# RUN npm install next

# EXPOSE 3000
# CMD ["npm", "start"]



FROM node:18-alpine AS base
FROM base AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

ENV PORT=3000
CMD ["node", "server.js"]