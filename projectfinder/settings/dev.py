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
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
