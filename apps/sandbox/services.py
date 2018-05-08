import requests

_API = 'https://transkribus.eu/TrpServer/rest'
_USER_AGENT = 'TranskribusWebUI'
_OPTIONS = {
    'verify': True,
    'stream': False
}

_FIELDS = {
    'userName': ('username', str),
    'firstname': ('first_name', str),
    'lastname': ('last_name', str),
    # 'isAdmin': ('is_superuser', boolean),
    'isAdmin': ('is_staff', boolean),
    'sessionId': ('session_id', str),
    'loginTime': ('login_time', str),
    'userAgent': ('user_agent', str),
    'userId': ('user_id', int),
    'isActive': ('is_active', boolean),
    # 'ip': ('ip', str)
    # 'email': ('email', str),
}

def serialize_user_info(data):
    user_info = data.pop('trpUserLogin', {})

    for field_name in _FIELDS:
        value = user_info.pop(field_name, None)
        if value is not None:
            mapped_field_name, serialize = _FIELDS[field_name]
            user_info[mapped_field_name] = serialize(value)

    return user_info

def boolean(value):
    if value == 'true':
        return True
    elif value == '1':
        return True
    elif value == '0':
        return False
    else:
        return False

def is_valid(session_id):

    url = "{host}/auth/checkSession".format(
        host=_API.rstrip('/'))

    r = requests.get(
        url,
        headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'},
        **_OPTIONS
    )

    return r.status_code == 200

def login(username, password):

    url = "{host}/auth/login".format(
        host=_API.rstrip('/'))

    r = requests.post(
        url,
        data={'user': username, 'pw': password},
        headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'},
        **_OPTIONS
    )

    if r.status_code == 200:
        if r.headers['Content-Type'].lower().startswith('application/json'):
            return serialize_user_info(r.json())
        else:
            raise NotImplementedError("Unknown content type encountered: {!s}".format(r.headers['Content-Type']))
    else:
        r.raise_for_status()
    return None
