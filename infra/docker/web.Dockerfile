FROM node:22-alpine AS build

WORKDIR /app

COPY apps/web/package.json apps/web/package-lock.json apps/web/tsconfig.json apps/web/tsconfig.node.json apps/web/vite.config.ts ./
COPY apps/web/index.html ./index.html
COPY apps/web/src ./src
COPY apps/web/public ./public

RUN npm ci \
    && npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY infra/nginx/web.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
