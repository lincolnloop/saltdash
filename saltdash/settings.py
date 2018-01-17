"""
Django settings for saltdash project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from distutils.util import strtobool
import logging.config

import dj_database_url
from django.urls import reverse_lazy
from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = strtobool(os.getenv('DEBUG', 'false'))

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'raven.contrib.django.raven_compat',
    'social_django',

    'saltdash.dash',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'saltdash.core.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'saltdash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'saltdash.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {'default': dj_database_url.config('DATABASE_URL')}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


RAVEN_CONFIG = {'dsn': os.getenv('SENTRY_DSN')}

# Disable Django's logging setup
LOGGING_CONFIG = None

LOGLEVEL = os.getenv('LOGLEVEL', 'info').upper()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        },
    },
    'handlers': {
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        # Add Handler for Sentry for `warning` and above
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'WARNING',
            'handlers': ['console', 'sentry'],
        },
        # Our application code
        'saltdash': {
            'level': LOGLEVEL,
            'handlers': ['console', 'sentry'],
            # Avoid double logging because of root logger
            'propagate': False,
        },
    },
}
# Add runserver request logging back in
for k in ['formatters', 'handlers', 'loggers']:
    LOGGING[k]['django.server'] = DEFAULT_LOGGING[k]['django.server']
try:
    # setup pretty logging for local dev
    import readable_log_formatter
    LOGGING['formatters']['default'] = {
        '()': 'readable_log_formatter.ReadableFormatter'
    }
except ImportError:
    pass
logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, os.pardir, 'client', 'dist')
]
STATIC_ROOT = os.path.join(BASE_DIR, os.pardir, 'static')

# Python Social Auth
AUTHENTICATION_BACKENDS = [
    'social_core.backends.github.GithubTeamOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

SOCIAL_AUTH_URL_PREFIX = 'auth'
# Bypass LoginRequiredMiddleware for social auth login and callback
LOGIN_EXEMPT_URLS = [f'{SOCIAL_AUTH_URL_PREFIX}/.*']
LOGIN_URL = reverse_lazy('social:begin', args=['github-team'])
LOGIN_REDIRECT_URL = '/'


# create token https://github.com/settings/tokens
# curl -H "Authorization: token <token>" \
#       https://api.github.com/orgs/<org>/teams
SOCIAL_AUTH_GITHUB_TEAM_ID = os.environ['GITHUB_TEAM_ID']

# https://github.com/organizations/<org>/settings/applications
SOCIAL_AUTH_GITHUB_TEAM_KEY = os.environ['GITHUB_TEAM_KEY']
SOCIAL_AUTH_GITHUB_TEAM_SECRET = os.environ['GITHUB_TEAM_SECRET']
# Need to read teams to know if user can login
SOCIAL_AUTH_GITHUB_TEAM_SCOPE = ['read:org']

if (not SOCIAL_AUTH_GITHUB_TEAM_ID or
        not SOCIAL_AUTH_GITHUB_TEAM_KEY or
        not SOCIAL_AUTH_GITHUB_TEAM_SECRET):
    log.warning("GitHub login environment variables not present. "
                "Turning off login requirement.")
    # If Github is not setup, don't require login
    MIDDLEWARE.remove('saltdash.core.middleware.LoginRequiredMiddleware')
