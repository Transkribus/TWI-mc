from .base import *

BASE_URL = '/read'

SECRET_KEY = 'secret'

DEBUG = False

ALLOWED_HOSTS = ['transkribus.eu']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
    }
}

STATIC_URL = BASE_URL + STATIC_URL
MEDIA_URL = BASE_URL +  MEDIA_URL

LOGIN_REDIRECT_URL = BASE_URL + '/library'
LOGOUT_REDIRECT_URL = BASE_URL + '/library'

SERVER_EMAIL = 'email@transkribus.eu'

ADMINS = [
    ('Rory', 'rory.mcnicholl@london.ac.uk'),
    ('Berthold', 'berthold.ulreich@alumni.uni-graz.at')
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
     'formatters': {
        'request': {
            # reformat your log messages if you fancy
            'format':'[%(asctime)s] - %(levelname)s - %(module)s : %(message)s',
            'datefmt' : '%d/%b/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'logfile': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'errors'),
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
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'),
        },
    },
}
