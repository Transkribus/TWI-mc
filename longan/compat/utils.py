from django.utils.translation import ugettext_lazy as _


def t_log(*args, **kwargs): pass


def t_gen_request_id(*args, **kwargs): pass

###########################################################
# crop(list coords, boolean offset=None)
# turn polygon coords into rectangle coords or xywh if offset flag set


def crop(coords, offset=None):
   # coords = region.get("Coords").get("@points")
    points = coords.split()
    xmin = ymin = 99999999  # TODO durh...
    xmax = ymax = 0
    points = [list(map(int, point.split(','))) for point in points]
    # boo two loops! but I like this one above here...
    # TODO woops... I actually need this to give the x-off y-off width and
    # height...
    for point in points:
        if point[1] > ymax:
            ymax = point[1]
        if point[1] < ymin:
            ymin = point[1]
        if point[0] > xmax:
            xmax = point[0]
        if point[0] < xmin:
            xmin = point[0]
    if offset:
        crop = {'x': xmin, 'y': ymin, 'w': (xmax - xmin), 'h': (ymax - ymin)}
    else:
        crop = {
            'tl': [
                xmin, ymin], 'tr': [
                xmax, ymin], 'br': [
                xmax, ymax], 'bl': [
                    xmin, ymax]}

    return crop


def get_role(request, collId):
    t = request.user.tsdata.t

    collections = t.collections(request)
    for collection in collections:
        if collection.get('colId') == int(collId):
            return collection.get('role')


def error_message_switch(request=None, x=0):
    return {
        # 401: _('Transkribus session is unauthorised, you must <a
        # href="'+request.build_absolute_uri(settings.SERVERBASE+"/logout/?next={!s}".format(request.get_full_path()))+'"
        # class="alert-link">(re)log on to Transkribus-web</a>.'),
        401: _('Transkribus session is unauthorised, you must log on to Transkribus-web.'),
        403: _('You are forbidden to request this data from Transkribus.'),
        404: _('The requested Transkribus resource does not exist.'),
        500: _('A Server error was reported by Transkribus.'),
        503: _('Could not contact the Transkribus service, please try again later.'),
    }.get(x, _('An unknown error was returned by Transkribus: ') + str(x))
