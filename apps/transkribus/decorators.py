from functools import wraps

from django.conf import settings
from django.contrib.auth import decorators
from django.contrib.auth import login, logout
from django.shortcuts import redirect

from requests.exceptions import HTTPError

from . import backends


def login_required(view_func, *args, **kwargs):

    view_func_with_login = decorators.login_required(view_func, *args, **kwargs)

    def wrapper(request, *args, **kwargs):
        try:
            if not request.user.is_authenticated():
                # Let default decorator handle this
                return view_func_with_login(request, *args, **kwargs)
            else:
                return view_func(request, *args, **kwargs)
        except HTTPError as error:
            if error.response.status_code in (401, 403):
                logout(request, next_page=request.get_full_path())
                return redirect('logout')
            else:
                raise error

    return wrapper

def login_required_with_cookie(view_func, key=None):

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated():
            user = backends.authenticate_with_cookie(request, key)
            if user is not None:
                login(request, user)
        return view_func(request, *args, **kwargs)

    return wrapper
