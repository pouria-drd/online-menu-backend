import os
from .env import *
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------
# Security & Debug Configuration
# ---------------------------------------------------------------
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV_DEBUG

# ---------------------------------------------------------------
# User and Authentication Configuration
# ---------------------------------------------------------------
AUTH_USER_MODEL = "users.UserModel"

AUTHENTICATION_BACKENDS = [
    "authentication.backends.AuthBackend",  # Custom authentication backend
    # "django.contrib.auth.backends.ModelBackend",  # Default Django authentication
]

# ---------------------------------------------------------------
# Installed Apps Configuration
# ---------------------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party apps
    "corsheaders",
    "django_filters",
    "rest_framework",
    "django_cleanup.apps.CleanupSelectedConfig",
    # Custom apps
    "users",
    "authentication",
    # "mailer",
    # "monitoring",
]

# ---------------------------------------------------------------
# Middleware Configuration
# ---------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware
    "django.middleware.security.SecurityMiddleware",  # Security middleware
    "django.contrib.sessions.middleware.SessionMiddleware",  # Session middleware
    "django.middleware.common.CommonMiddleware",  # Common middleware
    "django.middleware.csrf.CsrfViewMiddleware",  # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # Authentication middleware
    "django.contrib.messages.middleware.MessageMiddleware",  # Message middleware
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Prevent clickjacking
]

# ---------------------------------------------------------------
# Debug Toolbar Configuration
# ---------------------------------------------------------------
ENABLE_DEBUG_TOOLBAR = ENV_ENABLE_DEBUG_TOOLBAR
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")


# ---------------------------------------------------------------
# URL Configuration
# ---------------------------------------------------------------
ROOT_URLCONF = "online_menu_backend.urls"
WSGI_APPLICATION = "online_menu_backend.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ---------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "omb_db.sqlite3",
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = ENV_TIME_ZONE
USE_I18N = ENV_USE_I18N
USE_TZ = ENV_USE_TZ


# ---------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# Static files URL and root directory
STATIC_URL = ENV_STATIC_URL
STATIC_ROOT = os.path.join(BASE_DIR, ENV_STATIC_ROOT_NAME)

# Media files URL and root directory
MEDIA_URL = ENV_MEDIA_URL
MEDIA_ROOT = BASE_DIR / ENV_MEDIA_ROOT_NAME


# ---------------------------------------------------------------
# Allowed Hosts & Internal IPs
# ---------------------------------------------------------------
ALLOWED_HOSTS = ENV_ALLOWED_HOSTS
INTERNAL_IPS = ENV_INTERNAL_IPS


# ---------------------------------------------------------------
# CORS & CSRF Configuration
# ---------------------------------------------------------------
CORS_ALLOWED_ORIGINS = ENV_CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = ENV_CORS_ALLOW_CREDENTIALS
CSRF_TRUSTED_ORIGINS = ENV_CSRF_TRUSTED_ORIGINS

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]


# ---------------------------------------------------------------
# Django REST Framework Configuration
# ---------------------------------------------------------------
REST_FRAMEWORK = {
    # "DEFAULT_AUTHENTICATION_CLASSES": [
    #     "rest_framework_simplejwt.authentication.JWTAuthentication",
    # ],
    # "DEFAULT_PERMISSION_CLASSES": [
    #     "rest_framework.permissions.AllowAny",
    # ],
    # "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    # "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": ENV_ANON_THROTTLE_RATE,
        "user": ENV_USER_THROTTLE_RATE,
        "otp": ENV_OTP_THROTTLE_RATE,
    },
}


# ---------------------------------------------------------------
# Email Configuration
# ---------------------------------------------------------------
EMAIL_BACKEND = ENV_EMAIL_BACKEND
EMAIL_HOST = ENV_EMAIL_HOST
EMAIL_PORT = ENV_EMAIL_PORT
EMAIL_USE_TLS = ENV_EMAIL_USE_TLS
EMAIL_HOST_USER = ENV_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = ENV_EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = ENV_DEFAULT_FROM_EMAIL


# ---------------------------------------------------------------
# Simple JWT Configuration
# ---------------------------------------------------------------
minutes = ENV_MINUTES
hours = ENV_HOURS

SIMPLE_JWT = {
    # Access token lifetime
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=minutes),
    # Refresh token lifetime
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=hours),
    # Authentication header type
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Update last login time when refreshing token
    "UPDATE_LAST_LOGIN": True,
}

# ---------------------------------------------------------------
# Celery Configuration
# ---------------------------------------------------------------
CELERY_BROKER_URL = ENV_CELERY_BROKER_URL
CELERY_RESULT_BACKEND = ENV_CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = ENV_CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER = ENV_CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER = ENV_CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE = ENV_CELERY_TIMEZONE


# ---------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # ---------------------------------------------------------------
    # Formatters — define log formats
    # ---------------------------------------------------------------
    "formatters": {
        "json_formatter": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
        },
        "console_formatter": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    # ---------------------------------------------------------------
    # Handlers — define where logs are sent
    # ---------------------------------------------------------------
    "handlers": {
        # Console output for dev
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter" if DEBUG else "json_formatter",
            "level": "DEBUG" if DEBUG else "INFO",
        },
        # "general_file_handler": {
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "filename": LOG_DIR / "general.log",
        #     "maxBytes": 10 * 1024 * 1024,  # 10 MB per file
        #     "backupCount": 5,
        #     "formatter": "json_formatter",
        #     "level": "INFO",
        # },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB per file
            "backupCount": 3,
            "formatter": "json_formatter",
            "level": "ERROR",
        },
        "app_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB per file
            "backupCount": 5,
            "formatter": "json_formatter",
            "level": "INFO",
        },
    },
    # ---------------------------------------------------------------
    # Loggers — define what uses which handlers
    # ---------------------------------------------------------------
    "loggers": {
        # Django core
        # "django": {
        #     "handlers": ["console_handler", "general_file_handler"],
        #     "level": "INFO",
        #     "propagate": True,
        # },
        "django.request": {
            "handlers": ["error_file_handler", "app_file_handler"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        # "django.db.backends": {
        #     "handlers": ["console_handler", "error_file_handler"],
        #     "level": "ERROR",
        #     "propagate": False,
        # },
        # App-specific logger
        "app": {
            "handlers": [
                "app_file_handler",
                "error_file_handler",
            ],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        # Catch-all
        # "": {
        #     "handlers": [
        #         "console_handler",
        #         "general_file_handler",
        #         "error_file_handler",
        #     ],
        #     "level": "INFO",
        #     "propagate": False,
        # },
    },
}
