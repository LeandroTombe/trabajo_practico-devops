# Build de la app
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Servir con nginx + proxy dinámico
FROM nginx:alpine

# Instalar envsubst si no está disponible
RUN apk add --no-cache gettext

# Copiar template de configuración
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Copiar archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Variable de entorno por defecto para desarrollo
ENV API_URL=http://api:8000

# Script para procesar template y iniciar nginx
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-substitute-templates.sh && \
    echo 'envsubst "\$API_URL" < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.d/40-substitute-templates.sh && \
    chmod +x /docker-entrypoint.d/40-substitute-templates.sh

EXPOSE 80
