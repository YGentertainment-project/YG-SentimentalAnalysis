"""
Django settings for yg project.
Generated by 'django-admin startproject' using Django 4.0.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from utils.shortcuts import get_env
from datetime import datetime

# production_env = get_env("YG_ENV", "dev") == "production"
# if production_env:
#     from .production_settings import *
# else:
from .dev_settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(DATA_DIR, "config", "secret.key"), "r") as f:
    SECRET_KEY = f.read()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

VENDOR_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'account',
    'clipping',
    'config',
    'crawler',
    'report',
    'utils'
]

INSTALLED_APPS = VENDOR_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yg.urls'

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

WSGI_APPLICATION = 'yg.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True  # 데이터베이스 저장 시에도 현재시간(Asia/Seoul)대로 저장되도록 설정

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATICFILES_DIRS = [BASE_DIR/"public",]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# # Rabbitmq env_values
# RABBITMQ_HOSTS = os.environ.get('RABBITMQ_HOST', 'localhost')
# RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'ygenter')
# RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD', 'ygenter')
# RABBITMQ_QUEUE_EXPIRES = 300.0  # seconds
# RABBITMQ_MESSAGE_EXPIRES = RABBITMQ_QUEUE_EXPIRES

# LOG_PATH = os.path.join(DATA_DIR, "log")

# LOGGING_HANDLERS = ['serverfile']

# REQUEST_LOGGING_ENABLE_COLORIZE=False
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'standard': {
#             'format': '[%(asctime)s] - [%(levelname)s] - [%(name)s:%(lineno)d]  - %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         }
#     },
#     'handlers': {
#         'serverfile': {
#             'level': 'DEBUG',
#             'encoding': 'utf-8',
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': os.path.join(LOG_PATH, f"{datetime.today().strftime('%Y-%m-%d')}.log"),
#             'when': "midnight",
#             'interval': 1,
#             'formatter': 'standard',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': LOGGING_HANDLERS,
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         '': {
#             'handlers': LOGGING_HANDLERS,
#             'level': 'WARNING',
#             'propagate': True,
#         }
#     },
# }

# REST_FRAMEWORK = {
#     'TEST_REQUEST_DEFAULT_FORMAT': 'json',
#     'DEFAULT_RENDERER_CLASSES': (
#         'rest_framework.renderers.JSONRenderer',
#     )
# }

IP_HEADER = "HTTP_X_REAL_IP"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS_ORIGIN_WHITELIST = (
#     "http://localhost:8000",
#     "http://127.0.0.1:8000",
# )

# IMPORT_EXPORT_USE_TRANSACTIONS = True
