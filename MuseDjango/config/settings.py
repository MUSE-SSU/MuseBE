from datetime import timedelta
from pathlib import Path
import os
import my_settings

STAGE = os.environ.get("STAGE", "DEV")
if STAGE == "DEV":
    DEV = True
    DEBUG = True
elif STAGE == "PROD":
    DEV = False
    DEBUG = False
else:  # for unintentional case
    DEBUG = False
    DEV = False

MUSE_SLACK_TOKEN = my_settings.MUSE_SLACK_TOKEN

DATABASES = my_settings.DATABASES
SECRET_KEY = my_settings.SECRET_KEY
SECRET_ALGORITHM = my_settings.SECRET_ALGORITHM

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    #
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # 'rest_auth.registration',
    "allauth.socialaccount.providers.kakao",
    # Site
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third Party
    "django_celery_beat",
    "django_celery_results",
    "django_crontab",
    "corsheaders",
    "storages",
    "taggit",
    "taggit_serializer",
    "rest_framework",
    "rest_framework.authtoken",
    # "rest_framework_jwt",
    # 'rest_auth',
    # MY APP
    "accounts",
    "musepost",
    "topics",
    "notice",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://muse.seoul.kr",
    "https://muse.seoul.kr",
)

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # [os.path.join(BASE_DIR, "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Celery Settings
CELERY_ALWAYS_EAGER = False
CELERY_BROKER_URL = "redis://redis:6379"
# CELERY_RESULT_BACKEND = "redis://redis:6379"
CELERY_ACCEPT_CONTENT = ["application/json", "json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Seoul"
CELERY_ENABLE_UTC = False
# CELERY_RESULT_BACKEND_MAX_RETRIES = 1
CELERY_TASK_IGNORE_RESULT = True

# Django Server Settings
LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_L10N = True
USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # 'rest_framework.authentication.TokenAuthentication',
        # "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # my authentication
        "common.authentication.MUSEAuthenticationForWeb",
    ],
}

"""
JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': SECRET_ALGORITHM,
    'JWT_EXPIRATION_DELTA': timedelta(hours=12),    # 토큰 만료 시간 12시간
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(hours=10),  # Refresh 가능한 시간
}

REST_USE_JWT = True
"""

AUTH_USER_MODEL = "accounts.User"


"""
# Image Upload To MEDIA
# MEDIA_URL = "/media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "media")
"""

# Image Upload To AWS S3
AWS_ACCESS_KEY_ID = my_settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = my_settings.AWS_SECRET_ACCESS_KEY

AWS_REGION = "ap-northeast-2"
AWS_STORAGE_BUCKET_NAME = my_settings.AWS_STORAGE_BUCKET_NAME

AWS_S3_HOST = "s3.ap-northeast-2.amazonaws.com"
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"

AWS_DEFAULT_ACL = "public-read"
# AWS_S3_SECURE_URLS = False
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

AWS_STATIC_LOCATION = "static"
STATICFILES_STORAGE = "config.asset_storage.StaticStorage"
STATIC_URL = "https://{}/{}/".format(AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)

AWS_PUBLIC_MEDIA_LOCATION = "media/public"
DEFAULT_FILE_STORAGE = "config.asset_storage.PublicMediaStorage"
MEDIA_URL = "https://{}/{}/".format(AWS_S3_CUSTOM_DOMAIN, AWS_PUBLIC_MEDIA_LOCATION)

AWS_PRIVATE_MEDIA_LOCATION = "media/private"
PRIVATE_FILE_STORAGE = "config.asset_storage.PrivateMediaStorage"

# ADMIN_MEDIA_PREFIX = '/static/admin/'
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_S3_SIGNATURE_VERSION = "s3v4"

# HashTag 대소문자 구별 안함
TAGGIT_CASE_INSENSITIVE = True
TAGGIT_LIMIT = 30

# Log
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "api": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
