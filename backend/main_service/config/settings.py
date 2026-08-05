import os
from datetime import timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [value.strip() for value in os.environ.get(name, default).split(',') if value.strip()]


SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-only')
DEBUG = env_bool('DEBUG', True)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

ALLOWED_HOSTS = env_list(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,main-service',
)

AUTH_USER_MODEL = 'accounts.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.vk',
    'dj_rest_auth',
    'dj_rest_auth.registration',

    'accounts',
    'excursions',
    'bookings',
    'reviews',
    'wishlist',
    'analytics',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

_cors_origins = env_list(
    'CORS_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,'
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
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', False)
SECURE_CONTENT_TYPE_NOSNIFF = True

ROOT_URLCONF = 'config.urls'

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

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Omsk'
USE_I18N = True
USE_TZ = True

WSGI_APPLICATION = 'config.wsgi.application'

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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

INTERNAL_IPS = ['127.0.0.1']

SPECTACULAR_SETTINGS = {
    'TITLE': 'API «КОЛЕСО путешествий 55»',
    'DESCRIPTION': 'Полная документация REST API туристической компании «КОЛЕСО путешествий 55». '
                   'Каталог экскурсий, бронирование, оплата и личный кабинет.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',

    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
        'displayRequestDuration': True,
        'tryItOutEnabled': True,
    },

    'REDOC_UI_SETTINGS': {
        'hideHostname': True,
        'hideDownloadButton': False,
        'showExtensions': True,
        'hideSingleRequestSampleTab': False,
        'docExpansion': 'none',
        'defaultModelRendering': 'example',
        'defaultModelExpandDepth': 1,
        'pathInMiddlePanel': False,
        'payloadSampleIdx': 0,
    },

    'COMPONENT_SPLIT_REQUEST': True,
}

SITE_ID = 1

ACCOUNT_LOGIN_METHOD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_LOGIN_METHODS = {'email'}

ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_PASSWORD_MIN_LENGTH = 8

ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = False

ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = False

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': False,
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        },
    },
    'vk': {
        'SCOPE': ['email'],
    }
}

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'webmaster@localhost')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Custom email templates
ACCOUNT_EMAIL_CONFIRMATION_SUBJECT = 'Подтверждение email - КОЛЕСО путешествий 55'
ACCOUNT_PASSWORD_RESET_SUBJECT = 'Сброс пароля - КОЛЕСО путешествий 55'

REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'access',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh',
    'JWT_AUTH_HTTPONLY': False,
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.UserProfileSerializer'
}

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Omsk'
CELERY_ENABLE_UTC = True
CELERY_TASK_DEFAULT_RETRY_DELAY = 60     # Пауза перед повтором: 60 секунд
CELERY_TASK_MAX_RETRIES = 3              # Максимум попыток
CELERY_TASK_ACKS_LATE = True             # Подтверждение ПОСЛЕ выполнения
CELERY_WORKER_PREFETCH_MULTIPLIER = 1    # Брать по 1 задаче за раз
CELERY_TASK_IGNORE_RESULT = True         # Не хранить результаты задач
CELERY_TASK_DEFAULT_QUEUE = 'django'
CELERY_TASK_DEFAULT_EXCHANGE = 'django'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'django'
# CELERY_TASK_ROUTES = {
#     'accounts.tasks.send_verification_email_task': {'queue': 'email'},
# }

# Domain configuration for email links
DOMAIN = os.environ.get('DOMAIN', 'localhost:8001')
PROTOCOL = os.environ.get('PROTOCOL', 'http')
RECOMMENDER_BASE_URL = os.environ.get('RECOMMENDER_BASE_URL', 'http://recommender_api:8000')
