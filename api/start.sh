#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
python manage.py migrate --check || (
    echo "Ejecutando migraciones..."
    python manage.py migrate
)

echo "Creando superusuario si no existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
" || echo "Error creando superusuario, continuando..."

echo "Iniciando servidor..."
exec gunicorn api_project.wsgi:application --bind 0.0.0.0:8000 --workers 2