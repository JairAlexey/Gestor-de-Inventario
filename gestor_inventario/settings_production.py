from .settings import *  # noqa: F403, F401
import dj_database_url

DEBUG = False

# Configura tu dominio de Railway aquí
ALLOWED_HOSTS = [
    'gestor-de-inventario-production.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1'
]

# Configuración CSRF para Railway
CSRF_TRUSTED_ORIGINS = [
    'https://gestor-de-inventario-production.up.railway.app',
    'https://*.railway.app',
]

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:uFDkaUsLEMdKHBkUXZouSgPlkLRsHiAT@hopper.proxy.rlwy.net:47733/railway',
        conn_max_age=600,
        ssl_require=True
    )
}

# Seguridad adicional para producción
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
