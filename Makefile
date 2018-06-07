.PHONY: migrations

PYTHON_VERSION ?= 3.6
PIP := pip${PYTHON_VERSION}
PYTHON := python${PYTHON_VERSION}
APP_MAIN := twi-mc
APP_SETTINGS := config.settings.production

debug:
	echo ${PYTHON_VERSION}

virtualenv:
	python${PYTHON_VERSION} -m venv venv

install: packages migrations check

packages: requirements.txt
	${PIP} install -r requirements.txt

check:
	${PYTHON} manage.py check --settings=config.settings.production --deploy

migrations:
	export DJANGO_SETTINGS_MODULE=${APP_SETTINGS}
	${PYTHON} manage.py makemigrations transkribus
	${PYTHON} manage.py makemigrations home
	${PYTHON} manage.py makemigrations sandbox
	${PYTHON} manage.py makemigrations waffle
	${PYTHON} manage.py migrate

mostlyclean:
	${PIP} freeze | xargs ${PIP} uninstall -y

clean: mostlyclean
	# TODO: flush database, drop tables, remove migrations
	echo -e "Not Implemented!\a"
