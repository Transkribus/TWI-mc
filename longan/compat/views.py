from django.http import HttpResponseRedirect

from .utils import error_message_switch

# error pages (where not handled by modals)


def error_view(request, response):
    return error_switch(request, response.status_code)


def error_switch(request, x):
    # If transkribus session becomes unauthorised we need to remove it from the userobject, so we don't get stuck in a 401 state for ever...
    # if x == 401 :
    #      TSData.objects.get(user=request.user).delete()

    return {
        401: HttpResponseRedirect(
            request.build_absolute_uri(
                getattr(settings, 'BASE_URL') + "/login?error=401&next=".format(
                    request.get_full_path()))), 403: render(
            request, 'error.html', {
                'msg': error_message_switch(
                    request, 403)}), 404: render(
            request, 'error.html', {
                'msg': error_message_switch(
                    request, 404)}), 500: render(
            request, 'error.html', {
                'msg': error_message_switch(
                    request, 500)}), 503: render(
            request, 'error.html', {
                'msg': error_message_switch(
                    request, 503)}), }.get(
        x, render(
            request, 'error.html', {
                'msg': error_message_switch(x)}))
