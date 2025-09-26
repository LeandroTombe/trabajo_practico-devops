# Build de la app
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# Servir con nginx + proxy dinámico
FROM nginx:alpine

# Copiar template de configuración (nginx lo procesará automáticamente)
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Copiar archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Variable de entorno por defecto para desarrollo
ENV API_URL=http://api:8000

EXPOSE 80
