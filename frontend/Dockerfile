FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage - just copy files, nginx will be in separate container
FROM alpine:latest

RUN apk add --no-cache rsync

# Copy built files to a location we can access
COPY --from=builder /app/dist /app/dist

# Entrypoint script to copy files to volume
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'rsync -av /app/dist/ /usr/share/nginx/html/' >> /entrypoint.sh && \
    echo 'exec sleep infinity' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

WORKDIR /usr/share/nginx/html

ENTRYPOINT ["/entrypoint.sh"]
