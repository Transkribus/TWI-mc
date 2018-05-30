import os
import sys

from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(BASE_DIR))
sys.path.append(BASE_DIR)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS += [
    'collections',
    'transkribus',
    'sandbox',
    # 'utils',
    # 'dashboard',
    # 'edit',
    # 'search',
    # 'review',
    # 'navigation'
]

INSTALLED_APPS += [
    'waffle',
    'bootstrap3',
    'captcha'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'waffle.middleware.WaffleMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

ROOT_URLCONF = 'longan.urls'

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
                # 'utils.contexts.appname',
                # 'utils.contexts.urlname',
		# 'utils.contexts.apphead',
		# 'utils.contexts.nav_up',
		# 'utils.contexts.version',
		# 'utils.contexts.browser_list',
                # 'utils.contexts.static_url', 
            ],
            'libraries' : {
                # 'read_tags': 'utils.templatetags',
            },
        },
    },

]

WSGI_APPLICATION = 'longan.wsgi.application'

AUTH_USER_MODEL = 'transkribus.User'

AUTHENTICATION_BACKENDS = [
    'transkribus.backends.TranskribusBackend',
    'transkribus.backends.ModelBackend',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/library'
LOGOUT_REDIRECT_URL = '/library'

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

#Added for READ locale directory for translations
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_CODE = 'en'

LANGUAGES = [
    # ('bg', _('Bulgarian')),
    # ('hr', _('Croatian')),
    # ('cs', _('Czech')),
    # ('da', _('Danish')),
    # ('nl', _('Dutch')),
    ('en', _('English')),
    # ('et', _('Estonian')),
    ('fi', _('Finnish')),
    ('fr', _('French')),
    ('de', _('German')),
    ('el', _('Greek')),
    # ('hu', _('Hungarian')),
    # ('ga', _('Irish')),
    # ('it', _('Italian')),
    # ('lv', _('Latvian')),
    # ('lt', _('Lithuanian')),
    # ('mt', _('Maltese')), NO MALTESE IN DJANGO!
    # ('pl', _('Polish')),
    # ('pt', _('Portuguese')),
    # ('ro', _('Romanian')),
    # ('sk', _('Slovak')),
    # ('sl', _('Slovenian')),
    ('es', _('Spanish')),
    ('sv', _('Swedish')),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = 'collected_static'
STATIC_URL = '/static/'

MEDIA_ROOT = 'media'
MEDIA_URL =  '/media/'

PAGE_SIZE_DEFAULT = 5

TRP_URL = 'https://transkribus.eu/TrpServer/rest/'

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

USE_CDNS = True

CDNS = {
    'bootstrap_css' : {
        'local': 'css/bootstrap.min.css',
        'cdn' : 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.1/css/bootstrap.min.css'
    },
    'bootstrap_js' : {
        'local': 'js/bootstrap.min.js',
        'cdn' : '//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'
    },
    'datatables_css' : {
        'local': 'css/jquery.dataTables.min.css',
        'cdn': '//cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css'
    },
    'datatables_js' : {
        'local': 'js/jquery.dataTables.min.js',
        'cdn': '//cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js'
    },
    'jquery' : {
        'local' : 'js/jquery.js',
        'cdn': '//code.jquery.com/jquery-1.12.3.js'
    },
    'jquery_ui' : {
        'local' : 'js/jquery-ui.min.js',
        'cdn': '//code.jquery.com/ui/1.12.1/jquery-ui.min.js'
    },
    'jquery_ui_css' : {
        'local' : 'css/jquery-ui.css',
        'cdn' : '//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css'
    },
    'chart_js' : {
        'local': 'js/Chart.bundle.min.js',
        'cdn': '//cdnjs.cloudflare.com/ajax/libs/Chart.js/2.3.0/Chart.bundle.min.js'
    },
    'bootstrap_notify_css' : {
        'local' : 'css/bootstrap-notify.min.css',
        # This cdn may be out of date!
        'cdn': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-notify/0.2.0/css/bootstrap-notify.min.css'
    },
    'bootstrap_notify_js' : {
        'local' : 'js/bootstrap-notify.min.js',
        'cdn': '//cdnjs.cloudflare.com/ajax/libs/mouse0270-bootstrap-notify/3.1.7/bootstrap-notify.min.js'
    },
    'bootstrap_select_css' : {
        'local' : 'css/bootstrap-select.min.css',
        'cdn': '//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/css/bootstrap-select.min.css'
    },
    'bootstrap_select_js' : {
        'local' : 'js/bootstrap-select.min.js',
        'cdn' : '//cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.12.4/js/bootstrap-select.min.js'
    },
    'js_cookie' : {
        'local' : 'js/js.cookie.min.js',
        'cdn' : '//cdnjs.cloudflare.com/ajax/libs/js-cookie/2.2.0/js.cookie.min.js'
    },
}


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

WORKFLOWS = {
    'linear' : {
        'perms':  ['CrowdTranscriber','Transcriber'],
        'statuses': ['IN_PROGRESS', 'DONE']
    },
    'free': {
        'perms' : ['Editor', 'Owner', 'Admin'],
        'statuses' : ['IN_PROGRESS', 'DONE', 'FINAL']
    },
    'default' : {
        'perms' : ['Reader'],
        'statuses' : None
    },
    # 'uber-free' : {
    #     'perms' : ['Admin'],
    #     'statuses' : ['NEW', 'IN_PROGRESS', 'DONE', 'FINAL', 'GT']
    # }
}

INTERFACES = {'i': ['edit', 'view'], 'lbl': [], 'sbs' : [], 't': [] }
