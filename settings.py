# -*- coding:utf-8 -*-
# Import default settings from memopol core
# Then override if needed
from memopol.base.default_settings import *   # pylint: disable=W0614,W0401

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'
LANGUAGES = (
  ('fr', 'French'),
  ('en', 'English'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%fg8-eo$qpi_@7tjdn^jdjx8mfp=(t=jbb@09y+zj$0ufj$v2g'

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

ADMINS = (
    ('memopol', 'contact@lqdn.fr'),
)
MANAGERS = ADMINS
DEFAULT_FROM_EMAIL = 'memopol@lqdn.fr'
INTERNAL_IPS = ('127.0.0.1',)
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

#==============================================================================
# Calculation of directories relative to the project module location
#==============================================================================

import os

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, "static_deploy", "static")
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'uploads')
MEDIA_DIRECTORY = MEDIA_ROOT  # FIXME: remove
MEMOPOL_TMP_DIR = os.path.join(PROJECT_DIR, "tmp")  # FIXME: more generic name needed
if not os.path.exists(MEMOPOL_TMP_DIR):
    os.makedirs(MEMOPOL_TMP_DIR)


#==============================================================================
# Project URLS and media settings
#==============================================================================

ROOT_URLCONF = 'memopol.base.urls'

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'

#==============================================================================
# Templates
#==============================================================================

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

#==============================================================================
# Middleware
#==============================================================================

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

#==============================================================================
# Current project instance settings
#==============================================================================
CACHES = {
    'default': dict(
        BACKEND='django.core.cache.backends.%s' % ('locmem.LocMemCache' if not DEBUG else 'dummy.DummyCache'),
        OPTIONS={
            'MAX_ENTRIES': 1000000000,
        }
    )
}

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'crontab': {
            'format':
                '%(levelname)s %(asctime)s %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARN',
            'class': 'logging.StreamHandler',
        },
        'crontab': {
            'level': DEBUG and 'DEBUG' or 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'crontab',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'memopol.base': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': True,
        },
        'crontab': {
            'handlers': ['crontab'],
            'level': DEBUG and 'DEBUG' or 'INFO',
            'propagate': True,
        },
        'search': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/memopol2.sqlite' % PROJECT_DIR,
    },
}

#==============================================================================
# Third party app settings
#==============================================================================


#==============================================================================
# Make it possible to locally override some settings
#==============================================================================

try:
    from settings_local import *
except ImportError:
    pass
