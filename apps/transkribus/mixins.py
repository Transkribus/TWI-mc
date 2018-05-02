from django.contrib.auth import mixins
from django.utils.decorators import method_decorator

from . import decorators

@method_decorator(decorators.login_required, 'dispatch')
class LoginRequiredMixin(mixins.LoginRequiredMixin):
    pass

@method_decorator(decorators.login_required_with_cookie, 'dispatch')
class LoginRequiredWithCookieMixin(mixins.LoginRequiredMixin):
    pass
