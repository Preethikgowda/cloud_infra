# ---- Build Stage ----
FROM node:20-alpine AS builder

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_APP_NAME=IntelliWealth

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_NAME=$VITE_APP_NAME

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --silent

COPY . .
RUN npm run build

# ---- Production Stage ----
FROM nginx:1.27-alpine

LABEL maintainer="IntelliWealth Engineering <engineering@intelliwealth.io>"
LABEL service="frontend"

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/nginx-health || exit 1

CMD ["nginx", "-g", "daemon off;"]
