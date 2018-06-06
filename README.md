# Longan
 Next verion of transkribus web interfaces

## Clean

Uninstall everything:

```bash
pip freeze | xargs pip uninstall -y
```

## Dependencies

```bash
pip install -r requirements.txt -t third_party
```

## Configuration

If you're mainly interested in running the application locally for testing or development, what `config/settings/local.py` is most likely what you're looking for. In that case you can skip to the [section on migrations section](#database-migrations).

Create `config/settings/secret.py` like so:
```python
SECRET_KEY = 'your-secret-key'
```

Review `config/settings/production.py`:

```python
ALLOWED_HOSTS = ['your-domain-goes-here']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
    },
    'UIBK': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
    }
}

RECAPTCHA_PUBLIC_KEY = 'your-public-key'
RECAPTCHA_PRIVATE_KEY = 'your-private-key'
```

## Database Migrations

To set up and run (with the local development environment):

```bash
python manage.py makemigrations transkribus
python manage.py makemigrations home
python manage.py makemigrations sandbox
python manage.py makemigrations waffle
python manage.py migrate
```

## Create Admin

```bash
python manage.py createsuperuser
```

## Static Files

```bash
python manage.py collectstatic
```

## Populate Test Database

Obtain database dump for most recent commit of _models.py_.

```
python manage.py loaddata db-${COMMIT}.json
```

## Run

### Production

```bash
ln longan/wsgi.py mc/wsgi.py
```

NOTE: This might not work with apache mod_wsgi.

### Local

```bash
export DJANGO_SETTINGS_MODULE=longan.settings.local
python manage.py runserver --settings=longan.settings.local
```
