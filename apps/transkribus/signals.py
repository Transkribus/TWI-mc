from django.conf import settings
from django.contrib.auth.signals import user_logged_out


def handle_log_out(sender, request, user):
    services.logout(user.transkribus.session_id)

user_logged_out.connect(handle_log_out)
