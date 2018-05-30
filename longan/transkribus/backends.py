import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import transaction

from . import models
from . import services


class TranskribusBackend(ModelBackend):
    """
    Transkribus authentication backend.

    Provides authentication backend for Transkribus REST API.

    This is a refactored version of the backend implementation created
    for TranskribusWebUI: https://github.com/Transkribus/TranskribusWebUI

    Creates Django user if it does not already exists.

    Updates fields for exising Django users.

    Also, stores and update Transkribus specific data in UserInfo
    associated with Django user.
    """

    def authenticate(self, request, username=None, password=None):

        if not username or not password:
            logging.debug("Discarding invalid username or password for user %s", username)
            return None

        data = services.login(username, password)

        if not data:
            return None

        user = create_or_update_user(data)

        return user

@transaction.atomic
def create_or_update_user(data):

    try:
        user = models.User.objects.get(
            username=data['username'])
    except models.User.DoesNotExist:
        user = models.User.create(**data)
        models.UserData.create(owner=user, **data)
        logging.debug("Created new user %s with pk %s", user.username, user.pk)
        return user

    else:
        user.update(**data)

    user_data, created = models.UserData.objects.get_or_create(owner=user)
    user_data.update(**data)

    logging.info("Login from %s as %s", data.get('ip'), data.get('username'))

    return user

def authenticate_with_cookie(request, key=None):

    if key is None:
        key = getattr(
            settings, 'TRANSKRIBUS_SESSION_KEY', 'JSESSIONID')

    session_id = request.COOKIES.get(key)
    if session_id is None:
        return None

    if not services.is_session_valid(session_id):
        return None

    data = services.get_data(session_id)

    user = create_or_update_user(data)
    return user
