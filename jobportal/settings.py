import os
from pathlib import Path


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
# EMAIL - RESEND HTTP API
# =========================================================

RESEND_API_KEY = os.environ.get(
    "RESEND_API_KEY",
    "",
)

if RESEND_API_KEY:

    DEFAULT_FROM_EMAIL = (
        "onboarding@resend.dev"
    )

else:

    DEFAULT_FROM_EMAIL = (
        "noreply@localhost"
    )


# Django's normal email backend is not used
# for Resend. The actual email sending is
# handled through Resend's HTTPS API in
# accounts/services.py.

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
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


# =========================================================
# PRODUCTION SECURITY
# =========================================================

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


# =========================================================
# RENDER
# =========================================================

RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    "RENDER_EXTERNAL_HOSTNAME",
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