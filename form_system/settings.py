import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-secret-key-in-production')
IS_RAILWAY = bool(
    os.getenv('RAILWAY_ENVIRONMENT', '').strip()
    or os.getenv('RAILWAY_PROJECT_ID', '').strip()
    or os.getenv('RAILWAY_SERVICE_ID', '').strip()
    or os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
)
DEBUG = os.getenv('DEBUG', '0' if IS_RAILWAY else '1').lower() in {'1', 'true', 'yes', 'on'}

ALLOWED_HOSTS = []
raw_allowed_hosts = os.getenv('ALLOWED_HOSTS', '').strip()
if raw_allowed_hosts:
    ALLOWED_HOSTS.extend([h.strip() for h in raw_allowed_hosts.split(',') if h.strip()])
railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
if railway_domain:
    ALLOWED_HOSTS.append(railway_domain)
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'smartforms',
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
]

ROOT_URLCONF = 'form_system.urls'

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

WSGI_APPLICATION = 'form_system.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{(BASE_DIR / 'db.sqlite3').as_posix()}",
        conn_max_age=int(os.getenv('CONN_MAX_AGE', '60')),
    )
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Africa/Cairo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

CSRF_TRUSTED_ORIGINS = []
raw_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()
if raw_csrf:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in raw_csrf.split(',') if o.strip()])
if railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_domain}')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

if IS_RAILWAY and not DEBUG and SECRET_KEY == 'replace-this-secret-key-in-production':
    raise RuntimeError('Missing SECRET_KEY environment variable in production')
