FROM node:24-slim

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY artifacts/api-server/package.json ./artifacts/api-server/package.json
COPY lib/api-spec/package.json ./lib/api-spec/package.json
COPY lib/api-zod/package.json ./lib/api-zod/package.json
COPY lib/api-client-react/package.json ./lib/api-client-react/package.json
COPY lib/db/package.json ./lib/db/package.json
COPY scripts/package.json ./scripts/package.json

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm --filter @workspace/api-server run build

ENV NODE_ENV=production \
    PORT=80

EXPOSE 80

CMD ["node", "--enable-source-maps", "artifacts/api-server/dist/index.mjs"]
