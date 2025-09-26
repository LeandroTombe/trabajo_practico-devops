import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"

# Para producción en Render
ALLOWED_HOSTS = [
    "localhost", 
    "127.0.0.1",
    "tp-redis-api.onrender.com",
    "tp-redis-web.onrender.com",
    ".onrender.com",  # Permite todos los subdominios de Render
]

# En producción, agregar hosts desde variable de entorno
if os.environ.get("RENDER"):
    ALLOWED_HOSTS.append(os.environ.get("RENDER_EXTERNAL_HOSTNAME"))

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.auth",        # ← necesario (Permission vive acá)
    "django.contrib.contenttypes",
    "django.contrib.sessions",    # ← middleware abajo
    "django.contrib.staticfiles",
    "rest_framework",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "api_project.urls"
WSGI_APPLICATION = "api_project.wsgi.application"

# Base de datos - configuración para Render con PostgreSQL
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

TIME_ZONE = "UTC"
USE_TZ = True

STATIC_URL = "static/"

CORS_ALLOW_ALL_ORIGINS = True

# Configuración de Redis para Render
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

# Cache con Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Configuración de sesiones
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}
