from datetime import timedelta
from pathlib import Path
import os
import my_settings

DATABASES = my_settings.DATABASES
SECRET_KEY = my_settings.SECRET_KEY
SECRET_ALGORITHM = my_settings.SECRET_ALGORITHM

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# APPS_DIR = os.path.join(BASE_DIR, 'myapps')

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    ".ap-northeast-2.compute.amazonaws.com",
    "*",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # MY APP
    "accounts",
    "musepost",
    "topics",
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
    #
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # 'rest_auth.registration',
    "allauth.socialaccount.providers.kakao",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Default primary key field type
# https://docs.dja@method_decorator(csrf_exempt)ngoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# personal add settings

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
# ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
# LOGIN_REDIRECT_URL = "/"
# ACCOUNT_AUTHENTICATED_LOGOUT_REDIRECTS = True
# ACCOUNT_LOGOUT_REDIRECT_URL = "/"

AUTH_USER_MODEL = "accounts.User"

CORS_ORIGIN_ALLOW_ALL = True

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
AWS_S3_SECURE_URLS = False
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

# Crontab
CRONJOBS = [
    ("*/1 * * * *", "musepost.cron.crontab_job", ">> ./logs/musepost_task.log"),
    ("*/1 * * * *", "musepost.cron.select_muse"),
]
