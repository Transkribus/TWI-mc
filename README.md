# TWI-mc
 Transkribus Web Interfaces: My collections site (python project)

```bash
git clone https://github.com/Transkribus/TWI-mc
cd TWI-mc
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
git pull
git submodule update --init

```

Make a file called `settings/local.py` and add

```python
from .base import *

SECRET_KEY = 'your-secret-goes-here'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'tmp/db.sqlite3'),
    }
}

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
VERSION = "My version String"
MILESTONE = 1
```

With approprate values (The last two may need to override/reset the defaults that are `mc/settings/production.py`)

To set up and run (with the default django dev environment):

```bash
python manage.py makemigrations transkribus waffle
python manage.py migrate
python manage.py collectstatic
export DJANGO_SETTINGS_MODULE=settings.local
python manage.py runserver --settings=settings.local

```