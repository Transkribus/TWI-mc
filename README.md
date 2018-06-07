# Longan
 Next verion of transkribus web interfaces


## Configuration


Create `config/settings/secret.py` like so:
```python
SECRET_KEY = 'your-secret-key'
```

Review the settings for you desired environment. For local development just use `local.py`. In most cases the settings will probably work without any making any changes.

To set up the application for production use `config/settings/production.py`:

```python
ALLOWED_HOSTS = ['your-domain-goes-here']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'tmp/db.sqlite3'),
    }
}

RECAPTCHA_PUBLIC_KEY = 'your-public-key'
RECAPTCHA_PRIVATE_KEY = 'your-private-key'
```

### Logging

When logging to a file make sure it's located at a location such as `/var/log/my-app/errors` rather than inside your project directory. Otherwise your webserver might end up with a file created by the web server that you are not permitted to move or delete.

## Setup

### Scripted

First, set you must set the Python version you would like to use, e.g.:

```bash
export PYTHON_VERSION=3.6
```

It is recommended that you also create a virtual environment:

```bash
make virtualenv
source venv/bin/activate
```

Then you can run:

```bash
make install
```

To verify that the project is set up correctly run:

```bash
make check
```

### Manual

#### Clean

Uninstall everything:

```bash
pip freeze | xargs pip uninstall -y
```

#### Dependencies

```bash
pip install -r requirements.txt -t third_party
```

#### Migrations

To set up and run (with the local development environment):

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py makemigrations transkribus
python manage.py makemigrations home
python manage.py makemigrations sandbox
python manage.py makemigrations waffle
python manage.py migrate
```

#### Create Admin

This is step does not apply to the local environment.

```bash
python manage.py createsuperuser
```

### Static Files

```bash
python manage.py collectstatic
```

### Populate Test Database

Obtain database dump for most recent commit of _models.py_.

```
python manage.py loaddata db-${COMMIT}.json
```
