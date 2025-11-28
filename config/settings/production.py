# import os
from .common import *


DEBUG = False
ENABLE_DEBUG_TOOLBAR = False

# ---------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "prod_db.sqlite3",
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": os.getenv("POSTGRES_DB"),
#         "USER": os.getenv("POSTGRES_USER"),
#         "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
#         "HOST": os.getenv("POSTGRES_HOST"),
#         "PORT": os.getenv("POSTGRES_PORT", "5432"),
#     }
# }


# ---------------------------------------------------------------
# Allowed Hosts & Internal IPs
# ---------------------------------------------------------------
INTERNAL_IPS = ["localhost", "127.0.0.1"]
ALLOWED_HOSTS = [
    "example.com",
    "www.example.com",
    "sub.example.com",
]

# ---------------------------------------------------------------
# CORS & CSRF Configuration
# ---------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://example.com",
    "https://api.example.com",
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# ---------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# ---------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
        },
        "console_formatter": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        },
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
            "level": "INFO",
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "json_formatter",
            "level": "ERROR",
        },
        "app_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json_formatter",
            "level": "INFO",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["error_file_handler", "app_file_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["app_file_handler", "error_file_handler"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
