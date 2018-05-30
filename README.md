# TWI-mc
 Longan: Transkribus web interfaces

## Configuration

Make a file called `settings/local.py` and add:

```python
from .base import *

SECRET_KEY = 'your-secret-key-goes-here'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
    }
}

RECAPTCHA_PUBLIC_KEY = 'your-public-key'
RECAPTCHA_PRIVATE_KEY = 'your-private-key'
```

## Database Migrations

To set up and run (with the local development environment):

```bash
python manage.py makemigrations transkribus
python manage.py makemigrations sandbox
python manage.py makemigrations waffle
python manage.py migrate

```

## Static Files

```bash
python manage.py collectstatic
```

## Run

### Local

```bash
export DJANGO_SETTINGS_MODULE=settings.local
python manage.py runserver --settings=settings.local
```