"""
Django settings for mc project.

Generated by 'django-admin startproject' using Django 1.10.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(BASE_DIR))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False #TODO check correct ALLOWED_HOSTS settings for transkribus.eu

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
     'formatters': {
        'request': {
            'format':'[%(asctime)s] - %(levelname)s - %(module)s : %(message)s' , #reformat your log messages if you fancy
           'datefmt' : '%d/%b/%Y %H:%M:%S'

        },
    },
    'handlers': {
        'logfile': {
            'level': 'WARN',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR + "/logfile",
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
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARN'), #change this for more or fewer log messages
        },
    },
}
ALLOWED_HOSTS = ['transkribus.eu']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
#Supporting apps
    'bootstrap3',
    'captcha',
#project app
    'mc',
#READ apps
    'apps.utils',
    'apps.library',
#    'review',
    'apps.dashboard',
    'apps.edit',
    'apps.search',
    'apps.navigation'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #Added for READ
    'django.middleware.locale.LocaleMiddleware',

]
#'django.contrib.auth.middleware.SessionAuthenticationMiddleware' ??

ROOT_URLCONF = 'mc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, '../templates'),  ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #Added for READ
                'apps.utils.contexts.appname',
                'apps.utils.contexts.urlname',
		'apps.utils.contexts.apphead',
		'apps.utils.contexts.nav_up',
		'apps.utils.contexts.version',
		'apps.utils.contexts.browser_list',
            ],
            'libraries' : {
                'read_tags': 'apps.utils.templatetags',
            },
        },
    },
]



WSGI_APPLICATION = 'mc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../tmp/db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

#Added for READ locale directory for translations
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

LANGUAGE_CODE = 'en'
#Added for READ lang set == official EU languages
from django.utils.translation import ugettext_lazy as _
LANGUAGES = [
#        ('bg', _('Bulgarian')),
#        ('hr', _('Croatian')),
#        ('cs', _('Czech')),
#        ('da', _('Danish')),
#        ('nl', _('Dutch')),
        ('en', _('English')),
#        ('et', _('Estonian')),
        ('fi', _('Finnish')),
        ('fr', _('French')),
        ('de', _('German')),
        ('el', _('Greek')),
#        ('hu', _('Hungarian')),
#        ('ga', _('Irish')),
#        ('it', _('Italian')),
#        ('lv', _('Latvian')),
#        ('lt', _('Lithuanian')),
#       ('mt', _('Maltese')), NO MALTESE IN DJANGO!
 #       ('pl', _('Polish')),
 #       ('pt', _('Portuguese')),
#        ('ro', _('Romanian')),
#        ('sk', _('Slovak')),
#        ('sl', _('Slovenian')),
        ('es', _('Spanish')),
        ('sv', _('Swedish')),
];

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

#### NB this is the static files setting for the production apache server

SERVERBASE = '/read'

#Step 1: we store static files in project_root/static
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
#Step 2 we also store static files in static directories in the apps
# and these finders will find them for us
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
#Step 3 We run python manage.py collectstatic it will collect the static files from the locations defined above
# and store them in the location defined by STATIC_ROOT (cannot be the same as any of the STATFILES_DIRS)
STATIC_ROOT =  'collected_static'
MEDIA_ROOT = 'media' #not currently used
#Step 4 Finally we tell django how to serve the static files
STATIC_URL = SERVERBASE+'/static/'
MEDIA_URL =  SERVERBASE+'/media/' #not currently used

##################### Added for READ ###################


## Auth backend that logs in to transkribus.eu and extends the django.contrib.auth.User
AUTHENTICATION_BACKENDS = [
    'apps.utils.backends.TranskribusBackend',
]

#Location of TRP server for transkribus REST services
TRP_URL = 'https://transkribus.eu/TrpServer/rest/'

NOCAPTCHA = True

LOGIN_URL = 'login'

#Where to on login if no next param available?
LOGIN_REDIRECT_URL = SERVERBASE+'/library'

#Where to on logout if no next param available?
LOGOUT_REDIRECT_URL = SERVERBASE+'/library'

#Default for size of paged data
PAGE_SIZE_DEFAULT = 5

### Manage static resources ###

#Switch to use CDNs or local
USE_CDNS = True
# Static Resources (js css etc)
CDNS = {'bootstrap_css' : {'local': "css/bootstrap.min.css", 'cdn' : "//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" },
       'bootstrap_js' : {'local': "js/bootstrap.min.js", 'cdn' : "//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"},
       'datatables_css' : {'local': "css/jquery.dataTables.min.css", 'cdn': "//cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css"},
       'datatables_js' : {'local': "js/jquery.dataTables.min.js", 'cdn': "//cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"},
       'jquery' : {'local' : "js/jquery.js", 'cdn': "//code.jquery.com/jquery-1.12.3.js" },
       'jquery_ui' : {'local' : "js/jquery-ui.min.js", 'cdn': "//code.jquery.com/ui/1.12.1/jquery-ui.min.js" },
       'jquery_ui_css' : {'local' : "css/jquery-ui.css", 'cdn' : "//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css" },
       'chart_js' : {'local': "js/Chart.bundle.min.js", 'cdn': "//cdnjs.cloudflare.com/ajax/libs/Chart.js/2.3.0/Chart.bundle.min.js"},
       'bootstrap_notify_css' : {'local' : "css/bootstrap-notify.min.css", 'cdn': "//cdnjs.cloudflare.com/ajax/libs/bootstrap-notify/0.2.0/css/bootstrap-notify.min.css"}, #this cdn may be out of date!
       'bootstrap_notify_js' : {'local' : "js/bootstrap-notify.min.js", 'cdn': "//cdnjs.cloudflare.com/ajax/libs/mouse0270-bootstrap-notify/3.1.7/bootstrap-notify.min.js" },
    'bootstrap_select_css' : {'local' : "css/bootstrap-select.min.css", 'cdn': "//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/css/bootstrap-select.min.css"},
    'bootstrap_select_js' : {'local' : "js/bootstrap-select.min.js", 'cdn' : "//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/js/bootstrap-select.min.js"},
    'js_cookie' : {'local' : "js/js.cookie.min.js", 'cdn' : "//cdnjs.cloudflare.com/ajax/libs/js-cookie/2.2.0/js.cookie.min.js"},
      }


PROFILE_LOG_BASE = '/tmp/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 28800 #8 hours like Transkribus REST session

BROWSERS = [
		{"browser": "Chrome", "versions": ["60.x"]},
		{"browser": "Firefox", "versions": ["43.x", "45.x"]}
]


##########################################
# Permissions stuff, mostly for apps/edit
# but useful to be avilable for all apps
# To check on role/permisions etc
########################################

# Who can edit?
CAN_EDIT = ['Editor', 'Owner', 'Admin', 'CrowdTranscriber','Transcriber']
# Who can view?
CAN_VIEW = ['Editor', 'Owner', 'Admin', 'CrowdTranscriber','Transcriber', 'Reader']

##########################
# Definition of workflows
#
# - perms (list)    : a list of user types who are allowed to use this workflow
# - statuses (list)     : a list of the page statuses that this workflow offers

# Currently the workflows do not mix well between different types of users, it is either or... but that's OK for now

WORKFLOWS = {'linear' : {'perms' :  ['CrowdTranscriber','Transcriber'],
              'statuses' : ['IN_PROGRESS', 'DONE'] },
         'free' : { 'perms' : ['Editor', 'Owner', 'Admin'],
               'statuses' : ['IN_PROGRESS', 'DONE', 'FINAL'] },
         'default' : { 'perms' : ['Reader'],
                           'statuses' : None},
        }
#Another possible workflow could allow Amdmin users the rights to/from GT and NEW
#      'uber-free' : {'perms' : ['Admin'],
#               'statuses' : ['NEW', 'IN_PROGRESS', 'DONE', 'FINAL', 'GT']}

#Which interfaces are available for edit / view
#INTERFACES = {'edit' : ['i', 'lbl'] , 'view' : ['i', 'lbl', 'sbs', 't' ]}

INTERFACES = {'i': ['edit', 'view'], 'lbl': ['edit','view'], 'sbs' : ['view'], 't': ['view'] }



