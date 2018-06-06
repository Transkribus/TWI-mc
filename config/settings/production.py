from .base import *
from .secret import *

BASE_URL = '/read'

DEBUG = False

ALLOWED_HOSTS = ['transkribus.eu']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
        'OPTIONS': {
            'timeout': 60
        }
    }
}

DATABASE_ROUTERS = ['library.routers.TranskribusRouter']

STATIC_URL = '/'.join([BASE_URL, STATIC_URL])
MEDIA_URL = '/'.join([BASE_URL, MEDIA_URL])

LOGIN_REDIRECT_URL = '/'.join([BASE_URL, LOGIN_REDIRECT_URL])
LOGOUT_REDIRECT_URL = '/'.join([BASE_URL, LOGOUT_REDIRECT_URL])

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
     'formatters': {
        'request': {
            'format':'[%(asctime)s] - %(levelname)s - %(module)s : %(message)s',
            'datefmt' : '%d/%b/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'logfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('/var/logs/path/to/dir/errors'),
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'request',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter' : 'request',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}
