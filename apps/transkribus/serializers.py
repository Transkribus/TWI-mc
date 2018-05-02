import logging
import json

def boolean(value):
    if value == 'true':
        return True
    elif value == '1':
        return True
    elif value == '0':
        return False
    else:
        return False

FIELDS = {
    'userName': ('username', str),
    'firstname': ('first_name', str),
    'lastname': ('last_name', str),
    'email': ('email', str),
    'isActive': ('is_active', boolean),
    'isAdmin': ('is_staff', boolean),
    # 'isAdmin': ('is_superuser', boolean),
    'sessionId': ('session_id', str),
    'userId': ('user_id', int),
    'loginTime': ('login_time', str),
    'userAgent': ('user_agent', str),
    'affiliation': ('affiliation', str),
    'gender': ('gender', str),
    # 'created': ('created', datetime)
    # 'loginTime': ('created', datetime)
    # 'ip': ('ip', str)
    # 'email': ('email', str),
}

def parse_user_data(fileobj):

    parsed_user_data = {}

    user_data = json.load(fileobj)

    for field_name in FIELDS:
        value = user_data.pop(field_name, None)
        if value is not None:
            mapped_field_name, serialize = FIELDS[field_name]
            parsed_user_data[mapped_field_name] = serialize(value)

    return parsed_user_data
