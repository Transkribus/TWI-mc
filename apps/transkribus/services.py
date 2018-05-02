import requests
import logging
import json 

from collections import OrderedDict

from django.conf import settings

from . import serializers

# FIXME: handle timeout errors gracefully, e.g. when trying to log in
# requests.exceptions.Timeout is raised, requests.get(..., timeout=1000)

USER_AGENT = getattr(settings, 'TRANSKRIBUS_USER_AGENT', 'TranskribusWebUI')

HEADERS = {
    'Accept': 'application/json',
    'User-Agent': USER_AGENT
}

URL = getattr(settings, 'TRANSKRIBUS_URL', 'https://transkribus.eu/TrpServer/rest/').rstrip('/')

KEY = getattr(settings, 'TRANSKRIBUS_SESSION_KEY', 'JSESSIONID')


def login(username, password):

    r = requests.post(
        '{host}/auth/login'.format(host=URL),
        data={'user': username, 'pw': password},
        headers=HEADERS,
        verify=True,
        stream=True
    )

    if r.status_code != 200:
        r.raise_for_status()

    content_type = r.headers.get('Content-Type')

    if content_type is None:
        raise NotImplementedError("Missing content type")
    elif r.headers['Content-Type'].lower().startswith('application/json'):
            r.raw.decode_content = True
            return serializers.parse_user_data(r.raw)
    else:
        raise NotImplementedError("Unexpected content type: {!s}".format(r.headers['Content-Type']))

def is_session_valid(session_id):

    r = requests.get(
        '{host}/auth/checkSession'.format(host=URL),
        cookies={KEY: session_id},
        headers=HEADERS,
        verify=True,
        stream=True
    )

    return r.status_code == 200

def get_user_data(session_id):

    r = requests.get(
        '{host}/auth/details'.format(host=URL),
        cookies={KEY: session_id},
        headers=HEADERS,
        verify=True,
        stream=True
    )

    content_type = r.headers.get('Content-Type')

    if content_type is None:
        raise NotImplementedError("Missing content type")
    elif r.headers['Content-Type'].lower().startswith('application/json'):
            r.raw.decode_content = True
            return serializers.parse_user_data(r.raw)
    else:
        raise NotImplementedError("Unexpected content type: {!s}".format(r.headers['Content-Type']))

def logout(session_id):

    r = requests.post(
        '{host}/auth/logout'.format(host=URL),
        cookies={KEY: session_id},
        headers=HEADERS,
        verify=True,
        stream=True
    )

    assert r.status_code == 200
