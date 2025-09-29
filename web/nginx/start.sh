#!/bin/sh
set -e

echo "Iniciando frontend..."
echo "RENDER_ENV value: '$RENDER_ENV'"
echo "Available env vars:"
env | grep -E "(RENDER|API)" || echo "No RENDER/API vars found"

# En Render siempre usar configuración sin proxy
# (detectamos por hostname también como fallback)
if [ "$RENDER_ENV" = "true" ] || [ -n "$RENDER_EXTERNAL_HOSTNAME" ] || echo "$PWD" | grep -q "render"; then
    echo "Configurando para Render (sin proxy interno)"
    cp /etc/nginx/templates/render.conf.template /etc/nginx/conf.d/default.conf
    echo "Configuración Render aplicada"
else
    echo "Configurando para docker-compose (con proxy interno)"
    # Procesar template con variables de entorno
    envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
    echo "Configuración docker-compose aplicada"
fi

echo "Archivo de configuración generado:"
cat /etc/nginx/conf.d/default.conf

echo "Iniciando nginx..."
exec nginx -g "daemon off;"