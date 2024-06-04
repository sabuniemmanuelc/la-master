import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from hashids import Hashids

from django.contrib.auth import get_user_model  # noqa: F401

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, 'deploy/docker'))

SECRET_KEY = 'django-insecure-k-h!%y@ybyn$9bjim$_j=n^yc5e_i(a5zol0!ftwm(w%v=0!%_'

DEBUG = False

ALLOWED_HOSTS = ['*']

hashids = Hashids(salt='i(a5zol0!ftwm')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',
    # 'debug_toolbar',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_yasg',
    'corsheaders',
    'rangefilter',
    'phonenumber_field',
    'django_extensions',
    'django_admin_multiple_choice_list_filter',
    'django_admin_inline_paginator',
    'tinymce',
    'cities_light',
    'django_celery_beat',
    'django_celery_results',
    'notifications',
    'django.contrib.postgres',
    'adminsortable2',
    'apps.account',
    'apps.notification',
    'apps.billing',
    'apps.service',
    'apps.support',
    'apps.data',
    'apps.utils',
    'apps.search',
    'apps.favorites',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'apps.utils.middleware.CheckPaymentRequiredMiddleware',
    # 'apps.utils.middleware.TimezoneMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'https://legal-advice.quantimo.ru',
    'http://127.0.0.1:8000',
    'https://legal-data.tech',
    'https://test.legal-data.tech',
    'https://legaldata.us',
    'https://legaldata.ltd',
]
CORS_ALLOW_ALL_ORIGINS = False

ROOT_URLCONF = 'la.urls'

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

WSGI_APPLICATION = 'la.wsgi.application'
AUTH_USER_MODEL = 'account.Account'

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'apps.utils.authenticate.CustomAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {'anon': '1000/day', 'user': '1000/day'},
    # 'DEFAULT_PAGINATION_CLASS': 'apps.utils.pagination.CursorPaginationWithOrdering',
    # 'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('POSTGRES_HOST', '172.17.0.1'),
        'NAME': os.environ.get('POSTGRES_DB', 'la'),
        'USER': os.environ.get('POSTGRES_USER', 'la_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'LKM6U3rD'),
        'PORT': os.environ.get('POSTGRES_PORT', 5456),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'back_static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'common_static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'
# PHONENUMBER_DEFAULT_REGION = 'RU'
PHONENUMBER_DEFAULT_REGION = 'US'

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': int(os.environ.get('REDIS_PORT', 6379)),
    'db': int(os.environ.get('REDIS_DB', 0)),
    # 'password': 'password',
    'prefix': os.environ.get('REDIS_PREFIX', 'session'),
    'socket_timeout': int(os.environ.get('REDIS_SOCKET_TIMEOUT', 1)),
    'retry_on_timeout': bool(os.environ.get('REDIS_RETRY_ON_TIMEOUT', False)),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('CACHES_LOCATION', 'redis://127.0.0.1:6379/1'),
    }
}

APPEND_SLASH = False

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://127.0.0.1:6379')

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Europe/Ireland'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_RESULT_BACKEND = 'django-db'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "mail.privateemail.com"
EMAIL_USE_TLS = True
# 465 with SSL, 587/25 with TLS
EMAIL_PORT = 587
EMAIL_HOST_USER = "info@legal-data.tech"
EMAIL_HOST_PASSWORD = "^MY1Njh7kQ3$"

CITIES_LIGHT_APP_NAME = 'data'

NOTIFICATIONS_NOTIFICATION_MODEL = 'notification.Notification'
DJANGO_NOTIFICATIONS_CONFIG = {'USE_JSONFIELD': True}

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}

DOMAIN_URL = ''
ACCESS_APPS_WITHOUT_PAY = [
    'apps.account:v1',
    'apps.billing:v1',
    'apps.data:v1',
    'apps.notification:v1',
    'apps.service:v1',
    'apps.support:v1',
]
TRIAL_PERIOD_DAYS = 3
TRIAL_PERIOD_INVOICE_DAYS_BEFORE = -2
SUBSCRIPTION_PERIOD_DAYS = 30
SUBSCRIPTION_PERIOD_INVOICE_DAYS_BEFORE = -3
STRIPE_TEST_SECRET_KEY = 'sk_test_51Mue33Ge5j7Igp1mYMQnMPkM9w9f7yeGGimdxci6CHopuxd6YrpR92Wrf6Yhc4C8HGwyq4HGy3SZ5mLUckFfgl1x003GzSSKpP'
STRIPE_TEST_PUBLIC_KEY = 'pk_test_51Mue33Ge5j7Igp1mwDAE7a9FYDs5onVIFwi5T7kEHqSCTR6mIr9PJYeWhJT2tEAl1WMoOsxew9WXushxJYHeBwRK003y5Q4khC'
STRIPE_SECRET_KEY = STRIPE_TEST_SECRET_KEY
STRIPE_PUBLIC_KEY = STRIPE_TEST_PUBLIC_KEY
STRIPE_ENDPOINT_SECRET = ''

MR_ROBOT_ACCOUNT = None
DEFAULT_DOMAIN = 'https://legaldata.us'
DEFAULT_ACCOUNT_REAL_NAME = 'lawyer'
INVOICE_ENABLED = False

PIXEL_ID = '922622855725664'
ACCESS_TOKEN = 'EAASbMfCDFuUBO62TOT9O3xTOK0ZB4Ixgh93Embnv0CyLTJdmh8DCD3uygaNJIk0432GPlZBkp8l0O6TqaYQP04ndFmFDopPgUcMyBWW7KjPSlRESaSkMHbua6HhTpZBH7dZBjOwLZBSxEcZB10wIhH9xgMkwtxkWJkvzRJixpStHVqiLuGYeWPSN5frZB0L8zp32AZDZD'
GENERAL_SLEEP_TIME = 3
