from pathlib import Path
import os
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# BASE DIR
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================
SECRET_KEY = "django-insecure-ycn6j2e5^dpwa6em)f!t)a-i4+_(re1^uw1c2a&j+j+p+-ut^w"
DEBUG = True
ALLOWED_HOSTS = []

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", ""
).split(",")


# =========================
# APPLICATIONS
# =========================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Cloudinary
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "accounts.apps.AccountsConfig",
    "catalog.apps.CatalogConfig",
    "orders.apps.OrdersConfig",
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URL & TEMPLATES
# =========================
ROOT_URLCONF = "courseproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
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

WSGI_APPLICATION = "courseproject.wsgi.application"


# =========================
# DATABASE
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================
# AUTH / PASSWORDS
# =========================
AUTH_USER_MODEL = "accounts.User"

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


# =========================
# INTERNATIONALIZATION
# =========================
LANGUAGE_CODE = "ar"
TIME_ZONE = "Asia/Riyadh"

USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ar", "العربية"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]


# =========================
# STATIC FILES
# =========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================
# CLOUDINARY CONFIG
# =========================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


# =========================
# DEFAULT PK
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
