import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent 

load_dotenv()


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [value.strip() for value in os.environ.get(name, default).split(',') if value.strip()]


YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID')
CHROMA_PERSIST_DIR = os.environ.get(
    'CHROMA_PERSIST_DIR',
    os.path.join(BASE_DIR, 'chroma_data'),
)

SECRET_KEY = os.environ.get('ASSISTANT_SECRET_KEY', 'django-insecure-assistant-development-only')
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = env_list(
    'ASSISTANT_ALLOWED_HOSTS',
    'localhost,127.0.0.1,assistant-service',
)

# Убрали AUTH_USER_MODEL, так как assistant-service - отдельный проект без accounts app

INSTALLED_APPS = [
    # Убрали django.contrib.admin, так как assistant-service не нуждается в админке
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'assistant',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'koleso_travel_dev'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'sql'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
        'CONN_HEALTH_CHECKS': True,
    }
}

DB_SSLMODE = os.environ.get('DB_SSLMODE', 'prefer')
if DB_SSLMODE != 'disable':
    DATABASES['default']['OPTIONS'] = {'sslmode': DB_SSLMODE}
    if db_sslrootcert := os.environ.get('DB_SSLROOTCERT'):
        DATABASES['default']['OPTIONS']['sslrootcert'] = db_sslrootcert

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('ASSISTANT_REDIS_URL', 'redis://redis:6379/2'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
_cors_origins = env_list(
    'CORS_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173',
)
CORS_ALLOW_ALL_ORIGINS = DEBUG and '*' in _cors_origins
CORS_ALLOWED_ORIGINS = [origin for origin in _cors_origins if origin != '*']
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
