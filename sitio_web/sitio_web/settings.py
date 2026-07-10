"""
Configuración de Django para el proyecto corvimx.

Hardening aplicado para práctica escolar de ataque/defensa:
- Todas las variables sensibles se cargan desde .env (nunca hardcodeadas).
- DEBUG=False por defecto.
- ALLOWED_HOSTS y CSRF_TRUSTED_ORIGINS controlados por entorno (compatibles con ngrok).
- Cabeceras HTTP de seguridad activas.
- CSP estricta vía django-csp.
- Cookies de sesión/CSRF seguras.
- Logging robusto a consola y archivo.
"""

import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECURE_SSL_REDIRECT=(bool, False),
)
# Lee el archivo .env ubicado junto a manage.py (BASE_DIR)
environ.Env.read_env(BASE_DIR / '.env')

# ------------------------------------------------------------------
# Seguridad básica
# ------------------------------------------------------------------
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DJANGO_DEBUG')

ALLOWED_HOSTS = [
    h.strip() for h in env('DJANGO_ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in env('DJANGO_CSRF_TRUSTED_ORIGINS', default='').split(',')
    if o.strip()
]

# ------------------------------------------------------------------
# Apps y middleware
# ------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'csp',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    # Middleware propio de logging/seguridad (registro + detección de patrones sospechosos)
    'core.middleware.SecurityLoggingMiddleware',
]

ROOT_URLCONF = 'sitio_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sitio_web.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Monterrey'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# ------------------------------------------------------------------
# Cabeceras HTTP de seguridad
# ------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

# Necesario cuando la app corre detrás de un proxy que sí habla HTTPS (ngrok)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env('DJANGO_SECURE_SSL_REDIRECT')

# HSTS solo tiene sentido en producción real con HTTPS confirmado
if not DEBUG and SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False

# ------------------------------------------------------------------
# Cookies seguras
# ------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_HTTPONLY = False  # Debe ser legible por JS solo si tu frontend lo necesita; con templates Django no hace falta, pero se deja explícito
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG

# ------------------------------------------------------------------
# Content Security Policy (django-csp)
# Ajustada para permitir Bootstrap/Bootstrap Icons por CDN (jsdelivr)
# usados en base.html. Se evita 'unsafe-inline' en script-src; los
# scripts inline existentes deben migrarse a archivos .js estáticos.
# ------------------------------------------------------------------
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", 'https://cdn.jsdelivr.net'),
        'style-src': ("'self'", 'https://cdn.jsdelivr.net', "'unsafe-inline'"),
        'font-src': ("'self'", 'https://cdn.jsdelivr.net'),
        'img-src': ("'self'", 'data:'),
        'connect-src': ("'self'",),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
        'frame-ancestors': ("'none'",),
        'form-action': ("'self'",),
    }
}
# Nota: 'unsafe-inline' se mantiene solo en style-src porque Bootstrap y varios
# templates usan estilos inline puntuales. Si se eliminan esos estilos inline,
# se puede quitar 'unsafe-inline' de style-src también.

# ------------------------------------------------------------------
# Logging robusto
# ------------------------------------------------------------------
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file_general': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'file_security': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console', 'file_security'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Logger propio usado por core/middleware.py
        'core.security': {
            'handlers': ['console', 'file_security'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
