# Compila o TypeScript sem instalar Node.js na imagem final.
FROM node:22-alpine AS frontend
WORKDIR /app
COPY web/ ./web/
RUN npm install --no-save --no-package-lock --ignore-scripts typescript@5.9.3 \
    && ./node_modules/.bin/tsc --project web/tsconfig.json

FROM php:8.3-cli-bookworm
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
COPY --from=frontend /app/site/app.js /app/site/app.js
RUN mkdir -p /app/site \
    && chmod +x /app/docker/entrypoint.sh \
    && python3 scripts/build_site.py
EXPOSE 8080
ENV RUN_COLLECTION=0
CMD ["/app/docker/entrypoint.sh"]
