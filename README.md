# TWI-mc
 Transkribus Web Interfaces: My collections site (python project)

    git clone https://github.com/Transkribus/TWI-mc
    cd TWI-mc
    virtualenv -p /usr/bin/python3 .
    source bin/activate
    pip install -r requirements.txt
    git pull
    git submodule update --init

Make a file called `mc/settings/local.py` and add

    SECRET_KEY = '[somestuff]'

    RECAPTCHA_PUBLIC_KEY = ''
    RECAPTCHA_PRIVATE_KEY = ''

    SERVERBASE = ''
    STATIC_URL = SERVERBASE+'/static/'
    ALLOWED_HOSTS = ['127.0.0.1'] #or your local/dev server
    
    # To display the version string and link to the appropriate milestone set the following:
    VERSION = "My version String"
    MILESTONE = "1" # or whatever milestone you are on/working to

With approprate values (The last two may need to override/reset the defaults that are `mc/settings/production.py`)

To set up and run (with the default django dev environment):
    
    python manage.py makemigrations
    python manage.py makemigrations utils
    python manage.py migrate
    # possibly add python manage.py migrate utils
    python manage.py runserver [port]
