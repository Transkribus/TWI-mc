from django import template
from django.template.defaulttags import register
import datetime
import settings
from apps.utils.utils import error_message_switch

#register = template.Library()
@register.filter
def print_timestamp(timestamp):
    try:
        #assume, that timestamp is given in seconds with decimal point
        ts = float(timestamp)
    except ValueError:
        return None
    return datetime.datetime.fromtimestamp(ts/1000.0)

#register.filter(print_timestamp)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def coords_for_fimagestore(crop):
    return str(crop.get('x'))+"x"+str(crop.get('y'))+"x"+str(crop.get('w'))+"x"+str(crop.get('h'))

@register.filter
def coords_add_commas(coords):
    return coords.replace(" ",",")

@register.filter
def coords_for_imagemap(crop):
    return str(str(crop.get('tl')[0])+","+str(crop.get('tl')[1])+","+
        str(crop.get('tr')[0])+","+str(crop.get('tr')[1])+","+
        str(crop.get('br')[0])+","+str(crop.get('br')[1])+","+
        str(crop.get('bl')[0])+","+str(crop.get('bl')[1]))

@register.filter
def y_for_typewriterline(crop):
    return str(crop.get('tl')[1])

@register.filter
def load_lib(lib):
    if settings.USE_CDNS and lib in settings.CDNS:
        return str(settings.CDNS.get(lib).get('cdn'))
    return str(settings.CDNS.get(lib).get('local'))

@register.filter
def login_error_message(code):
    return error_message_switch(None,int(code))



