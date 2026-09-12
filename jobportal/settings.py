import os
from pathlib import Path

import dj_database_url


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


# =========================================================
# SECURITY
# =========================================================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "development-only-change-this-secret-key",
)

DEBUG = (
    os.environ.get(
        "DJANGO_DEBUG",
        "True",
    )
    .lower()
    == "true"
)

ALLOWED_HOSTS = [
    host.strip()
    for host
    in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


# =========================================================
# RENDER HOSTNAME
# =========================================================

RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME"
)

if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(
            RENDER_EXTERNAL_HOSTNAME
        )

    CSRF_TRUSTED_ORIGINS = [
        f"https://{RENDER_EXTERNAL_HOSTNAME}"
    ]

else:
    CSRF_TRUSTED_ORIGINS = []


# =========================================================
# APPLICATIONS
# =========================================================

INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts.apps.AccountsConfig",

]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [

    (
        "django.middleware.security."
        "SecurityMiddleware"
    ),

    "whitenoise.middleware.WhiteNoiseMiddleware",

    (
        "django.contrib.sessions."
        "middleware."
        "SessionMiddleware"
    ),

    (
        "django.middleware.common."
        "CommonMiddleware"
    ),

    (
        "django.middleware.csrf."
        "CsrfViewMiddleware"
    ),

    (
        "django.contrib.auth."
        "middleware."
        "AuthenticationMiddleware"
    ),

    (
        "django.contrib.messages."
        "middleware."
        "MessageMiddleware"
    ),

    (
        "django.middleware.clickjacking."
        "XFrameOptionsMiddleware"
    ),

]


ROOT_URLCONF = (
    "jobportal.urls"
)


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [

    {
        "BACKEND": (
            "django.template.backends."
            "django.DjangoTemplates"
        ),

        "DIRS": [
            BASE_DIR
            / "jobportal"
            / "templates"
        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                (
                    "django.template."
                    "context_processors."
                    "debug"
                ),

                (
                    "django.template."
                    "context_processors."
                    "request"
                ),

                (
                    "django.contrib.auth."
                    "context_processors."
                    "auth"
                ),

                (
                    "django.contrib.messages."
                    "context_processors."
                    "messages"
                ),

            ],

        },
    },

]


WSGI_APPLICATION = (
    "jobportal.wsgi.application"
)


# =========================================================
# DATABASE
# =========================================================

DATABASES = {

    "default": {

        "ENGINE": (
            "django.db.backends."
            "sqlite3"
        ),

        "NAME": (
            BASE_DIR
            / "db.sqlite3"
        ),

    }

}


# =========================================================
# RENDER POSTGRESQL DATABASE
# =========================================================

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)

if DATABASE_URL:

    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )


# =========================================================
# CUSTOM USER
# =========================================================

AUTH_USER_MODEL = (
    "accounts.User"
)


# =========================================================
# PASSWORD VALIDATORS
# =========================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": (
            "accounts.validators."
            "ComplexityPasswordValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "UserAttributeSimilarityValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "CommonPasswordValidator"
        )
    },

    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "NumericPasswordValidator"
        )
    },

]


# =========================================================
# INTERNATIONALIZATION
# =========================================================

LANGUAGE_CODE = (
    "en-us"
)

TIME_ZONE = (
    "Asia/Manila"
)

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = (
    "/static/"
)

STATICFILES_DIRS = [

    BASE_DIR
    / "jobportal"
    / "static"

]

STATIC_ROOT = (
    BASE_DIR
    / "staticfiles"
)


STORAGES = {

    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },

    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },

}


# =========================================================
# USER-UPLOADED MEDIA FILES
# =========================================================

MEDIA_URL = (
    "/media/"
)

MEDIA_ROOT = (
    BASE_DIR
    / "media"
)


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)


# =========================================================
# LOGIN
# =========================================================

LOGIN_URL = "/"

LOGIN_REDIRECT_URL = (
    "/dashboard/"
)


# =========================================================
# EMAIL
# =========================================================

EMAIL_HOST_USER = (
    os.environ.get(
        "GMAIL_ADDRESS",
        "",
    )
)

EMAIL_HOST_PASSWORD = (
    os.environ.get(
        "GMAIL_APP_PASSWORD",
        "",
    )
    .replace(
        " ",
        "",
    )
)


if (
    EMAIL_HOST_USER
    and EMAIL_HOST_PASSWORD
):

    EMAIL_BACKEND = (
        "django.core.mail.backends."
        "smtp.EmailBackend"
    )

    EMAIL_HOST = (
        "smtp.gmail.com"
    )

    EMAIL_PORT = 587

    EMAIL_USE_TLS = True

    EMAIL_TIMEOUT = 20

    DEFAULT_FROM_EMAIL = (
        EMAIL_HOST_USER
    )

else:

    EMAIL_BACKEND = (
        "django.core.mail.backends."
        "console.EmailBackend"
    )

    DEFAULT_FROM_EMAIL = (
        "noreply@localhost"
    )


# =========================================================
# COOKIE / SESSION SECURITY
# =========================================================

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = (
    "Lax"
)

CSRF_COOKIE_SAMESITE = (
    "Lax"
)


if not DEBUG:

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = (
        31536000
    )

    SECURE_HSTS_INCLUDE_SUBDOMAINS = (
        True
    )

    SECURE_HSTS_PRELOAD = True