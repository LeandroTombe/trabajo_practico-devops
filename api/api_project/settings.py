import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = ["*",]

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

# DB no se usa, pero Django lo requiere configurado
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TIME_ZONE = "UTC"
USE_TZ = True

STATIC_URL = "static/"

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}
