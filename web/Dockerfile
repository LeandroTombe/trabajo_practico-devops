# Build de la app
FROM node:20-alpine AS build
WORKDIR /app

# Argumento para la URL del API
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Servir con nginx
FROM nginx:alpine

# Copiar archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Script para seleccionar configuración según entorno
COPY nginx/start.sh /start.sh
RUN chmod +x /start.sh

# Copiar las dos configuraciones
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY nginx/render.conf.template /etc/nginx/templates/render.conf.template

# Variable de entorno por defecto para desarrollo
ENV API_URL=http://api:8000
ENV RENDER_ENV=false

EXPOSE 80

CMD ["/start.sh"]
