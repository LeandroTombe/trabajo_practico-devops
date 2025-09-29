#!/bin/sh
set -e

echo "Iniciando frontend..."

# Si estamos en Render, usar configuración sin proxy
if [ "$RENDER_ENV" = "true" ]; then
    echo "Configurando para Render (sin proxy interno)"
    cp /etc/nginx/templates/render.conf.template /etc/nginx/conf.d/default.conf
else
    echo "Configurando para docker-compose (con proxy interno)"
    # Procesar template con variables de entorno
    envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
fi

echo "Iniciando nginx..."
exec nginx -g "daemon off;"