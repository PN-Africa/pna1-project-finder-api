"""
Development settings for projectfinder.
"""
import os
from .common import *

DEBUG = True

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
    }
}

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
   
# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

MAILERS = {
    'default': {
        # 'BACKEND': 'django.core.mail.backends.console.EmailBackend',
        'BACKEND': 'anymail.backends.resend.EmailBackend',
    },
}

if os.getenv('USE_B2_STORAGE', 'False').lower() == 'true':
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': os.getenv('B2_APPLICATION_KEY_ID'),
                'secret_key': os.getenv('B2_APPLICATION_KEY'),
                'bucket_name': os.getenv('B2_BUCKET_NAME'),
                'region_name': os.getenv('B2_BUCKET_REGION', ''),
                'endpoint_url': os.getenv('B2_BUCKET_ENDPOINT_URL', ''),
                'file_overwrite': False,
                'default_acl': None,
                'querystring_auth': True,
                'querystring_expire': 3600,
            },
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }