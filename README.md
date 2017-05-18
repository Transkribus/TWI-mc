# TWI-mc
 Transkribus Web Interfaces: My collections site (python project)

    git clone https://github.com/Transkribus/TWI-mc
    git pull
    git submodule update --init

Make a file called `mc/settings/local.py` and add

    SECRET_KEY = '[somestuff]'

    RECAPTCHA_PUBLIC_KEY = ''
    RECAPTCHA_PRIVATE_KEY = ''

    SERVERBASE = ''
    STATIC_URL = SERVERBASE+'/static/'
    ALLOWED_HOSTS = ['127.0.0.1'] #or your local/dev server

With approprate values (The last two may need to override/reset the defaults that are `mc/settings/production.py`)
