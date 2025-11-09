"""
File: settings.py
Author: Reagan Zierke <reaganzierke@gmail.com>
Date: 2025-11-08
Description: Django settings for the project.
"""


from pathlib import Path
import os
from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("DJANGO_SECRET_KEY") or get_random_secret_key()
DEBUG = os.environ.get("DEBUG", "0") == "1"

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

raw_allowed = os.environ.get("ALLOWED_HOSTS", "")
if raw_allowed:
    ALLOWED_HOSTS = [h.strip() for h in raw_allowed.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = []

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_browser_reload",
    "django_vite",
    'django_crontab',
    'accounts',
    'market',
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
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PWD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

from urllib.parse import urlparse
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    result = urlparse(DATABASE_URL)
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': result.path.lstrip('/'),
        'USER': result.username,
        'PASSWORD': result.password,
        'HOST': result.hostname,
        'PORT': result.port,
    }

CRONJOBS = [
    ('* * * * *', 'django.core.management.call_command', ['update_stocks'], {}, '>> /tmp/cron_update_stocks.log 2>&1'),
    ('*/5 * * * *', 'django.core.management.call_command', ['random_market_event'], {}, '>> /tmp/cron_market_event.log 2>&1'),
]


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / "static" / "dist", BASE_DIR / "static" / "public" ]
STATIC_ROOT = BASE_DIR / "staticfiles"

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "static" / "public"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,  
        "manifest_path": BASE_DIR / "static" / "dist" / "manifest.json",
        "static_url_prefix": "/static/",
    }
}

if not DEBUG:
    DJANGO_VITE["default"]["manifest_path"] = str(STATIC_ROOT / "manifest.json")
    DJANGO_VITE["default"]["static_url_prefix"] = ""


