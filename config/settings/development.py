from .base import *

BASE_URL = '/readTest'

SECRET_KEY = 'enter-your-secret-here'

DEBUG = False

ALLOWED_HOSTS = ['transkribus.eu']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
    }
}

STATIC_URL = '/'.join([BASE_URL, STATIC_URL])
MEDIA_URL = '/'.join([BASE_URL, MEDIA_URL])

LOGIN_REDIRECT_URL = '/'.join([BASE_URL, LOGIN_REDIRECT_URL])
LOGOUT_REDIRECT_URL = '/'.join([BASE_URL, LOGOUT_REDIRECT_URL])

LOGGING = {
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter' : 'request',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}
