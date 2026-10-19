"""
Production settings for projectfinder.
Optimized for Docker deployments and Supabase PostgreSQL.
"""
import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production.")

allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_env.split(',') if h.strip()]

# Static files & WhiteNoise for production container deployments
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Production Database (Supabase PostgreSQL)
database_url = os.getenv('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '0')),
            conn_health_checks=True,
            ssl_require=os.getenv('DB_SSL_REQUIRE', 'True') == 'True',
        )
    }
elif os.getenv('DB_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.getenv('DB_NAME', 'postgres'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', ''),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', 'require'),
            },
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '0')),
            'CONN_HEALTH_CHECKS': True,
        }
    }

# Supabase pooler optimization:
# When using Supabase transaction pooler (port 6543), server-side cursors must be disabled
db_port = str(DATABASES['default'].get('PORT', ''))
if (
    os.getenv('DB_DISABLE_SERVER_SIDE_CURSORS', '').lower() in ('true', '1')
    or db_port == '6543'
):
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True

# Reverse proxy / Load balancer headers (Docker / Cloudflare / AWS / Render / Fly.io)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() == 'true'
CORS_ALLOW_CREDENTIALS = True

cors_origins_env = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in cors_origins_env.split(',')
        if origin.strip()
    ]

csrf_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in csrf_origins_env.split(',')
        if origin.strip()
    ]

# JWT secure cookies in production
REST_AUTH = {
    **REST_AUTH,
    'JWT_AUTH_SECURE': True,
}

# HTTPS and security headers
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Production email configuration using Django 6 MAILERS setting
_prod_email_backend = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
MAILERS = {
    'default': {
        'BACKEND': _prod_email_backend,
    },
}
