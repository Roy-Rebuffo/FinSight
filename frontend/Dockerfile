# ── Stage 1: Build ────────────────────────────────────────────────────
# Compilamos React en esta stage temporal
FROM node:22-alpine AS builder

WORKDIR /app

# Copiamos package.json primero para aprovechar el caché de Docker
COPY package.json package-lock.json ./
RUN npm ci

# Copiamos el resto y compilamos
COPY . .
RUN npm run build
# Genera la carpeta /app/dist con los ficheros estáticos optimizados

# ── Stage 2: Serve ────────────────────────────────────────────────────
# Solo copiamos el resultado del build, no el código fuente ni node_modules
# Imagen final mucho más pequeña
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80