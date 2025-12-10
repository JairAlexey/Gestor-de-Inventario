"""Settings para CI/Jenkins - Fuerza SQLite en lugar de PostgreSQL"""

from .settings import *

# Forzar base de datos SQLite en CI (no requiere servidor PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Relajar hosts para CI
ALLOWED_HOSTS = ["*"]

# Simula entorno de producción (pero sin PostgreSQL)
DEBUG = False

# Necesario para que Django resuelva URLs
ROOT_URLCONF = 'gestor_inventario.urls'

# Ruta donde Django guardará los archivos estáticos al hacer collectstatic
STATIC_ROOT = BASE_DIR / "staticfiles"
