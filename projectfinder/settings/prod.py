"""
Production settings for projectfinder.
Optimized for Docker deployments and Supabase PostgreSQL.
"""
import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [
    h.strip() 
    for h in os.getenv('DJANGO_ALLOWED_HOSTS').split(',') 
    if h.strip()
]

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '0')),
        conn_health_checks=True,
        ssl_require=True,
        # ssl_require=os.getenv('DB_SSL_REQUIRE', 'True') == 'True',
    )
}

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

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

# Dj Rest Auth JWT secure cookies
REST_AUTH = {
    **REST_AUTH,
    'JWT_AUTH_SECURE': True,
}

SIMPLE_JWT = {
    **SIMPLE_JWT,
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
}

# HTTPS and security headers
# SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

B2_CORE_CONFIG = {
    'access_key': os.getenv('B2_APPLICATION_KEY_ID'),
    'secret_key': os.getenv('B2_APPLICATION_KEY'),
    'bucket_name': os.getenv('B2_BUCKET_NAME'),
    'region_name': os.getenv('B2_BUCKET_REGION', ''),
    'endpoint_url': os.getenv('B2_BUCKET_ENDPOINT_URL', ''),
}

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            **B2_CORE_CONFIG,
            'location': 'media',
            'file_overwrite': False,
            'default_acl': None,
            'querystring_auth': True,
            'querystring_expire': 3600,
        },
    },
   'staticfiles': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            **B2_CORE_CONFIG,
            'location': 'static',
            'file_overwrite': True,
            'default_acl': None,
            'querystring_auth': False,
        }
    },
}

